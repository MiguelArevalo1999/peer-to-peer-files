import socket
import select
from time import sleep
import threading, queue
import random
# import STUN


class MRT:

    def __init__(self, addr):
        self.active_connections = None # port, address pair dict
        self.pending_connections = None # port, address pair list
        self.socket = None
        self.addr = addr

        # we use queue, because is synchronized.
        # we don't do any additional locking stuff.
        # The content are objects type of ClientPacket
        self.req_queue = queue.Queue()
        self.close = True  # closed state, not connected

    def sending_thread(self, recver):
        while not self.close:
            # print("Sending thread is running")
            while self.req_queue.empty():
                if self.close:
                    break
                sleep(0.1)  # 100 milliseconds
            while not self.close and not self.req_queue.empty():
                onePacket = self.req_queue.get()
                sent = self.sock.sendto(onePacket.pack(), self.addr)

        return  # finish when the sender is closed


    def mrt_accept1(self):
        data, client = self.sock.recvfrom(2048)

        connid = self.processData(client, data)

        return connid

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

    def mrt_open(self):
        # create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # bind to the address
        self.sock.bind(self.addr)

        return True

    def mrt_broadcast(self):

    def mrt_accept_file(self):

    def mrt_connect(self):


    def mrt_disconnect(self):

    def mrt_close(self):
        self.sock.close()



