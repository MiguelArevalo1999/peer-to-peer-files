import socket
import sys
from MRT import MRT
import threading
import time
import os


class Node:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    neighbors = []
    local_ip = 0
    local_port = 0
    public_ip = 0
    public_port = 0
    NAT_Type = None
    mrt = MRT()
    isOpen = False
    lock = threading.Lock()
    directory = ''

    # TODO (BRETT): Get Public IP and NAT Type
    def node_open(self, ip, port):
        self.mrt.mrt_open(ip, port)
        self.isOpen = True
        connection_thread = threading.Thread(target=self.node_accept)
        connection_thread.start()

    def node_accept(self):
        while self.isOpen:
            connections = self.mrt.mrt_accept_all()
            for conn in connections:
                self.lock.acquire()
                self.neighbors.append(conn)
                self.lock.release()
            time.sleep(1)

    def node_connect(self, ip, port):
        conn = self.mrt.mrt_connect(ip, port)
        self.lock.acquire()
        self.neighbors.append(conn)
        self.lock.release()

    # Disconnect from given connection
    def node_disconnect(self, ip, port):
        for neighbor in self.neighbors:
            # for each neighbor
            if neighbor[0] == ip and neighbor[1] == port:
                # if the neighbor is the specified connection
                self.mrt.mrt_disconnect(neighbor)
            # send the request to disconnect (disconnects if ACLS is received)

    # disconnect from given connection
    def node_close(self):
        self.mrt.mrt_close()
        self.isOpen = False

    def node_chat(self, msg):
        self.mrt.mrt_broadcast(msg)

    def node_broadcast_file(self, file_name):
        self.mrt.broadcast_file(file_name)

    def node_get_files(self):
        self.mrt.get_files()

    def node_request_file(self, file_name):
        self.mrt.request_file(file_name)
