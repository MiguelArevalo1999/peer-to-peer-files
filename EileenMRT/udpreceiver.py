import socket
import threading, queue
import logging
from time import sleep
import select
import sys
import os
import errno
from random import *

import consts as CONST
from packet import Packet
from clientmsg import ClientMessage

# we use queue, because is synchronized. 
# we don't do any additional locking stuff.
# The content are objects type of ClientPacket
packet_queue = queue.Queue()

    # This thread is consuming packets from a queue, 
    # and send them back the corresponding clients.
    # 
    # The main thread produces those packets.
def ack_thread(recver):
    while True:
        # print("Thread is running")
        while packet_queue.empty():
            sleep(0.1)       # 100 milliseconds
        while not packet_queue.empty():
            clientpacket = packet_queue.get()
            recver.mrt_sendpacket(clientpacket.client, clientpacket.packet)

# a class wrapping client address and packet
class ClientPacket:
    def __init__(self, client, packet):
        self.client = client
        self.packet = packet

# implement UDP protocol
class UdpReceiver:
    def __init__(self, addr, N):
        # server side variables
        self.sock = None
        self.N = N
        self.addr = addr    # server uses this address
        self.connSeqNo = 0      # used for connection IDs that are sent back to clients
        # # we use a FIFO queue to manage client connections
        # self.queue = queue.Queue(N)
        # we use a map to make sure a client uses a connection
        self.client_map = {}    # the key is tuple ('machine_addr', portno), the value is connectio id
        self.connid_client_map = {} # map connId to client addr
        self.clientmsgs = {}    # the key is tuple ('machine_addr', portno), the value is ClientMessage

        self.datacorrupt = False  # if it's on, generate random corruption, etc.
        self.packetloss = False # if it's on, lose random packets

    
    def setDataCorrupt(self, flag):
        self.datacorrupt = flag
        if flag:
            seed(11)
    def setPacketLoss(self, flag):
        self.packetloss = flag
        if flag:
            seed(11)

    # mrt_open: indicate ready-ness to receive incoming connections
    # addr is in format ('localhost', portnum)
    def mrt_open(self):
        # create a raw UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM )
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

        # bind to the address
        self.sock.bind(self.addr)

        # make the socket to non-blocking mode
        # # fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
        # self.sock.setblocking(0)
        # self.sock.settimeout(0)     # non-blocking mode

        return True

    def mrt_register(self, client):
        if client in self.client_map:
            return self.client_map[client]
        if len(self.client_map) > self.N:
            return -1
        else:
            connid = self.connSeqNo
            self.client_map.update({client: connid})
            self.connid_client_map.update({connid: client})
            self.connSeqNo += 1

            return connid

    # mrt_accept1: accept an incoming connection (return a connection), guaranteed to return one (will
    # block until there is one)
    def mrt_accept1(self):
        data, client = self.sock.recvfrom(CONST.BUFSIZE)

        connid = self.processData(client, data)
                
        return connid


    def mrt_sendpacket(self, client, packet):
        sent = self.sock.sendto(packet.pack(), client)
        # print('acknowledged {} bytes back to {}'.format(sent, client))

    def mrt_ack(self, client, type, connid):
        onePacket = Packet(connid, 0, type, 0, 0, "ACK")
        self.mrt_sendpacket(client, onePacket)

    # mrt_accept_all: accept all incoming connections (returns a possibly empty set/array of connections),
    # guaranteed not to block
    def mrt_accept_all(self):
        retids = []

        while True:
            socket_list = [self.sock]
            # nonblocking mode doesn't work on my environment
            # so I use select to check if the socket is readable
            readable_sockets, writeable_sockets, error_sockets = select.select(socket_list, [], [], 0.01)
            if self.sock in readable_sockets:
                # print("Socket is ready to read")
                connid = self.mrt_accept1()
                if connid > 0:  # a new connection
                    retids.append(connid)
            else:
                # print("No socket is ready to read")
                break

        return retids

    def processData(self, client, data):
        # let's unpack the data
        newPacket = Packet()
        newPacket.unpack(data)
        # print('received {} bytes from {}: type {}, frag# {}, data "{}"'.format(len(data), client, newPacket.type, newPacket.fragNum, newPacket.payload))
        connid = newPacket.connId

        #testing data corruption
        if self.datacorrupt and random() > 0.9:
            print("Corrupt data on fragnum ", newPacket.fragNum)
            newPacket.isValid = False

        #testing packet loss
        if self.packetloss and random() > 0.9:
            print("Lost packet fragnum: ", newPacket.fragNum)
            return connid

        if not newPacket.isValid:
            # corrupted data, ask to re-send
            onePacket = Packet(connid, 0, CONST.RSND, newPacket.fragNum, 0)
            packet_queue.put(ClientPacket(client, onePacket))
            return connid

        # the packet type should be RCON
        if newPacket.type == CONST.RCON:
            connid = self.mrt_register(client)
        
            if connid >= 0:
                onePacket = Packet(connid, 0, CONST.ACON, newPacket.fragNum, 0)
                packet_queue.put(ClientPacket(client, onePacket))
            else:
                onePacket = Packet(connid, 0, CONST.RSND, newPacket.fragNum, 0)
                packet_queue.put(ClientPacket(client, onePacket))

        elif newPacket.type == CONST.DATA or newPacket.type == CONST.RCLS:
            if not client in self.client_map: 
                # not connected yet
                onePacket = Packet(connid, 0, CONST.RSND, newPacket.fragNum, 0)
                packet_queue.put(ClientPacket(client, onePacket))

            if client in self.client_map:
                connid = self.client_map[client]
            else:
                return -1
            if newPacket.type == CONST.DATA:
                if not client in self.clientmsgs:
                    self.clientmsgs.update({client: ClientMessage(client)})
                self.clientmsgs[client].addPacket(newPacket)

                # got a good packet, ask for next one
                onePacket = Packet(connid, 0, CONST.ADAT, newPacket.fragNum, 0)
                packet_queue.put(ClientPacket(client, onePacket))
            else:
                if client in self.clientmsgs:
                    # check if there's any missing packets
                    missing = self.clientmsgs[client].checkMissingPackets(newPacket.fragNum)
                    if len(missing) > 0:
                        print("Missing packets {} from {}".format(','.join([str(i) for i in missing]), client))
                        onePacket = Packet(connid, 0, CONST.RSND, newPacket.fragNum, 0, ','.join([str(i) for i in missing]))
                        packet_queue.put(ClientPacket(client, onePacket))
                    else:
                        # got complete message
                        # need to compose the whole message
                        # and remove the connection and open up slot
                        size, msg = self.clientmsgs[client].constructMessage()
                        if len(msg) > 50:
                            samplemsg = (msg[0: 25] +' ... ' + msg[-25:]).encode("unicode_escape").decode("utf-8")
                        else:
                            samplemsg = msg.encode("unicode_escape").decode("utf-8")

                        print('Got complete message of size {} from {}. Sampling: "{}"'.format(size, client, samplemsg))
                        del self.client_map[client]
                        del self.clientmsgs[client]
                        onePacket = Packet(connid, 0, CONST.ACLS, newPacket.fragNum, 0, "")
                        packet_queue.put(ClientPacket(client, onePacket))
                else:
                    onePacket = Packet(connid, 0, CONST.ACLS, newPacket.fragNum, 0, "")
                    packet_queue.put(ClientPacket(client, onePacket))
        else:
            pass

        return connid
        


    # mrt_receive1: wait for at least one byte of data over a given connection, guaranteed to return data
    # except if the connection closes (will block until there is data or the connection closes)
    def mrt_receive1(self):
        data, client = self.sock.recvfrom(CONST.BUFSIZE)

        connid = self.processData(client, data)

        # connid = self.mrt_register(client)
        # # print("Connect ID=", connid)
        # if newPacket.valid():
        #     if connid >= 0:
        #         if not client in self.clientmsgs:
        #             self.clientmsgs.update({client: ClientMessage(client)})
                
        #         self.clientmsgs[client].addPacket(newPacket)

        #         if newPacket.final:
        #             # check missing packets
        #             missing = self.clientmsgs[client].checkMissingPackets()
        #             if len(missing) > 0:
        #                 onePacket = Packet(connid, 0, CONST.RSND, 0, 0, ','.join([str(i) for i in missing]))
        #                 packet_queue.put(ClientPacket(client, onePacket))
        #             else:
        #                 # got complete message
        #                 # need to compose the whole message
        #                 # and remove the connection and open up slot
        #                 print('Got complete message from {}'.format(client))
        #                 del self.client_map[client]
        #                 del self.clientmsgs[client]
        #                 onePacket = Packet(connid, 0, CONST.RCLS, 0, 0, "RCLS")
        #                 packet_queue.put(ClientPacket(client, onePacket))
        #         else:
        #             # got a good packet, ask for next one
        #             onePacket = Packet(connid, 0, CONST.ACON, 0, 0, "ACON")
        #             packet_queue.put(ClientPacket(client, onePacket))

        #     else:
        #         # no available slot, ask client to close or retry later
        #         onePacket = Packet(connid, 0, CONST.RCON, 0, 0, "RCON")
        #         packet_queue.put(ClientPacket(client, onePacket))
        # else:
        #     # corrupted data, ask client to resend
        #     onePacket = Packet(connid, 0, CONST.RSND, 0, 0, "-1")
        #     packet_queue.put(ClientPacket(client, onePacket))

        return connid    # return connId here

    
    # mrt_probe: given a set of connections, returns a connection in which there is currently data to be
    # received (may return no connection if there is no such connection, never blocks and ensures that a
    # mrt_receive1 call to the resulting connection will not block either)
    def mrt_probe(self):
        retids = []

        socket_list = [self.sock]
        # use select to check if the socket is readable
        readable_sockets, writeable_sockets, error_sockets = select.select(socket_list, [], [], 0.01)
        if self.sock in readable_sockets:
            retids.append(self.sock)

        return retids

    # # mrt_send: send a chunk of data over a given connection (may temporarily block execution if the
    # # receiver is busy/full)
    # def mrt_send(sock, connId, type, data):
    #     onePacket = Packet(connId, 0, type, 0, 0, data)
    #     sent = sock.sendto(onePacket.pack(), addr)
    #     retdata, server = sock.recvfrom(CONST.BUFSIZE)
    #     return retdata, server

    # mrt_close: close the connection
    def mrt_close(self):
        self.sock.close()

    # mrt_close: indicate incoming connections are no-longer accepted


# def thread_function(name):
#     logging.info("Thread %s: starting", name)
#     sleep(2)
#     logging.info("Thread %s: finishing", name)

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     logging.info("Main    : before creating thread")
#     x = threading.Thread(target=thread_function, args=(1,))
#     logging.info("Main    : before running thread")
#     x.start()
#     logging.info("Main    : wait for the thread to finish")
#     # x.join()
#     logging.info("Main    : all done")
    

