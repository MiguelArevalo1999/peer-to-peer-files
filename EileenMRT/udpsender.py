import socket
from time import sleep
import threading, queue
import select
import time
import os
from random import *

import consts as CONST
from packet import Packet

# implement UDP protocol
class UdpSender:
    def __init__(self, addr):
        # client side variables
        self.sock = None
        self.connId = -1
        self.addr = addr    # the server address
        self.close = True   # closed state, not connected

        # we use queue, because is synchronized. 
        # we don't do any additional locking stuff.
        # The content are objects type of ClientPacket
        self.req_queue = queue.Queue()

        self.window = {}    # use a dictionary for packet in currrnt window
                            # key is the fragnum, and value is the packet
        self.winSize = CONST.WINDOW_SIZE

        self.useRandomTest = False  # if it's on, generate random latency, etc.

    def setRandomTest(self, flag):
        self.useRandomTest = flag
        if flag:
            seed(11)

    def sending_thread(self, recver):
        while not self.close:
            # print("Sending thread is running")
            while self.req_queue.empty():
                if self.close:
                    break
                sleep(0.1)       # 100 milliseconds
            while not self.close and not self.req_queue.empty():
                onePacket = self.req_queue.get()
                if self.useRandomTest:
                    # generate random delay
                    sleep(random())
                sent = self.sock.sendto(onePacket.pack(), self.addr)

        return  # finish when the sender is closed

    # mrt_connect: sender connects to a given server (return a connection)
    # return a connection Id, which is the index in Queue (see the receiver code)
    def mrt_connect(self, data=""):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

        while True:
            onepacket = Packet(0, 0, CONST.RCON, 0, 0, data)

            # try to send first packet to receiver
            sent = self.sock.sendto(onepacket.pack(), self.addr)
            # Receiver may refuse the connection if the queue on receiver side is full
            retdata, server = self.sock.recvfrom(CONST.BUFSIZE)
            retPacket = Packet()
            retPacket.unpack(retdata)
            print('received {} bytes from {}: type {}'.format(len(retdata), server, retPacket.type))
            if retPacket.type != CONST.ACON:
                # try again
                continue
            else:
                self.connId = retPacket.connId
                break

        # now start a separate thread for sending data to the receiver
        self.close = False
        try:
            x = threading.Thread(target=self.sending_thread, args=(self,))
            x.start()
        except:
            print('Unable to start sending thread')

        return self.connId

    def printout_window(self):
        for fno in self.window:
            packet = self.window[fno]
            print("Win#{} packet type {}, data {}".format(fno, packet.type, packet.payload))
        return

    def resend_packets(self, idlist, fragno):
        print('Asked to resend "{}" or frag {}'.format(idlist, fragno))
        if len(idlist) > 0:
            ids = idlist.split(',')

            self.printout_window()

            for fno in ids:
                fragno = int(fno)
                # print("now resent packet #{}".format(fragno))
                if fragno in self.window:
                    print("Found packet {} to resend".format(fragno))
                    self.window[fragno].resetTimestamp()
                    self.req_queue.put(self.window[fragno])
        else:
            # just resend the last packet 
            if fragno in self.window:
                # print("now resent one packet #{}".format(fragno))
                self.req_queue.put(self.window[fragno])

        return                

    # mrt_send: send a chunk of data over a given connection (may temporarily block execution if the
    # receiver is busy/full)
    def mrt_send(self, fragnum, type=CONST.DATA, data=""):
        print('Sending type {} data "{}'.format(type, data.encode("unicode_escape").decode("utf-8")))
        onePacket = Packet(self.connId, 0, type, fragnum, 0, data)

        self.window.update({fragnum: onePacket})
        # sent = self.sock.sendto(onePacket.pack(), self.addr)
        # delegate to the sending thread 
        self.req_queue.put(onePacket)

        rettype = -1
        retdata = None

        while not self.close:
            socket_list = [self.sock]
            # nonblocking mode doesn't work on my environment
            # so I use select to check if the socket is readable
            # timeout 1 second
            readable_sockets, writeable_sockets, error_sockets = select.select(socket_list, [], [], 1)
            if self.sock in readable_sockets:
                retdata, server = self.sock.recvfrom(CONST.BUFSIZE)
                    
                retPacket = Packet()
                retPacket.unpack(retdata)
                rettype = retPacket.type
                retdata = retPacket.payload
                # print('received {} bytes from {}: type {}, fragnum {}'.format(len(retdata), server, retPacket.type, retPacket.fragNum))
                # here we check the return code
                if retPacket.type == CONST.ADAT:
                    # good, ready for sending next packet
                    # remove this packet from the window
                    if retPacket.fragNum in self.window:
                        del self.window[retPacket.fragNum]
                elif retPacket.type == CONST.ACLS:
                    self.mrt_disconnect()   # this sets self.close to True, so the outer while loop can stop
                    break
                elif retPacket.type == CONST.RSND:
                    print("Resend asked: retdata {} - fragnum {}".format(retdata, retPacket.fragNum))
                    # we either resend missing packets identified in retdata
                    # or just resend the last packet
                    self.resend_packets(retdata, retPacket.fragNum)

                    # we're requesting close the connection. 
                    # after missing packets have been set, we try again
                    if type == CONST.RCLS:
                        # the RCLS packet is still in current window
                        self.window[fragnum].resetTimestamp()
                        self.req_queue.put(self.window[fragnum])
                   
            # let's resend the old packet in this window
            currmillis = int(round(time.time() * 1000))
            if len(self.window) > 0:
                for fno in self.window:
                    if currmillis - self.window[fno].timestamp >= CONST.RETRY_TIMEOUT:
                        # delegate to the sending thread 
                        self.window[fno].resetTimestamp()
                        self.req_queue.put(self.window[fno])

            # if window is full, wait to receive any ACK from server
            if type == CONST.RCLS or len(self.window) >= CONST.WINDOW_SIZE:
                continue;
            else:
                # let's accept next packet
                # print("current type {}, and break out ".format(type))
                break

        return rettype, retdata

    # mrt_disconnect: close the connection
    def mrt_disconnect(self):
        self.close = True
        self.sock.close()

# send a file to receiver
# If the file is too, we need to split into chunks
def SendFile(server_addr, filepath):
    udp = None
    try:
        # if file doesn't exist or not accessible, exception will be thrown
        print("filepath =", filepath)
        filesize = os.path.getsize(filepath)
        print("filepath {}, filesize {}".format(filepath, filesize))
        f = open(filepath, "rb")

        # OK, file access is fine
        udp = UdpSender(server_addr)
        connid = udp.mrt_connect()
        print("ConnectId =", connid)
        
        num = 0
        bytes_read = f.read(CONST.CHUNK_SIZE)
        print("chunk # {}, chunksize {}".format(num, len(bytes_read)))
        while bytes_read:
            
            udp.mrt_send(num, CONST.DATA, bytes_read.decode('utf-8'))
            num += 1
            bytes_read = f.read(CONST.CHUNK_SIZE)
            print("chunk # {}, chunksize {}".format(num, len(bytes_read)))
        
        udp.mrt_send(num, CONST.RCLS)

    except Exception as ex:
        # file doesn't exist or not accessible
        print('Exception occurred "{}"'.format(str(ex)))
        return False
    finally:
        if udp:
            udp.mrt_disconnect()
        return True
