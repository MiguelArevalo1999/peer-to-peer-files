import socket
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

    #TODO (BRETT): Get Public IP and NAT Type
    def node_open(self, ip, port):
        self.mrt.mrt_open(ip, port)
        self.isOpen = True
        connection_thread = threading.Thread(target = self.node_accept)
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

	#Disconnect from given connection
    def node_disconnect(self, ip, port):
        for neighbor in self.neighbors:
            #for each neighbor
            if neighbor[0] == ip and neighbor[1] == port:
            #if the neighbor is the specified connection
                self.mrt.mrt_disconnect(neighbor)
                #send the request to disconnect (disconnects if ACLS is received)

	# Close connection
    def node_close(self, ip, port):
        self.mrt.mrt_close()

    def node_chat(self, msg):
        self.mrt.mrt_chat

	#Broadcast message. Create functions in MRT as neccesary
    # This is doing for each internal file in the directory, broadcast that we have that file.
    def node_broadcast(self, directory):
        if not directory:
            try:
                os.mkdir('./p2p_directory')
            except OSError:
                print('Directory creation failed')
                self.directory = './p2p_directory'
        else:
            self.directory = directory
            files = os.listdir(self.directory)
            for file in files:
                for conn in self.neighbors:
                    self.mrt.mrt_broadcast(conn, file)

	#Download file. May be multiple functions (request, get previous files, etc.). Create functions in MRT as neccesary.
	def node_download(self, filename):
		#TODO (SHANE)
        # Send requests for the names of files that each.
        for neighbor in self.neighbors:
            # Make the request message.

        # The neighbor will begin to send the file back to the user who broadcast the request. So we need to receive it.
        self.mrt.receiver_receive()





