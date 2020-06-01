import socket
import sys
from MRT import MRT
import threading
import time

class Node:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	neighbors = [] #not actually used ATM, everything handled in MRT.
	mrt = MRT()
	isOpen = False
	lock = threading.Lock()

	def node_open(self, ip, port, overWifi):
		self.mrt.mrt_open(ip, port, overWifi)
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

	def node_invite(self, ip, port):
		self.mrt.invite_connection((ip, port))

	def node_connect(self, ip, port):
		conn = self.mrt.mrt_connect(ip, port)
		self.lock.acquire()
		self.neighbors.append(conn)
		self.lock.release()

	def node_chat(self, msg):
		self.mrt.mrt_broadcast(msg)

	def node_broadcast_file(self, file_name):
		self.mrt.broadcast_file(file_name)

	def node_get_files(self):
		self.mrt.get_files()

	def node_request_file(self, file_name):
		self.mrt.request_file(file_name) 

	# # Close connection
	def node_close(self):
		self.mrt.mrt_close()
		self.isOpen = False


