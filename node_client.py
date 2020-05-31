import sys
sys.path.append('../')
from Node import Node

node = Node()
print('Enter IP')
myip = input('')
print('Enter Port')
myport = int(input(''))
node.node_open(myip, myport)
myUsername = string(input(''))

while True:
	msg = input('')
	if msg == 'Q':
		break
	elif msg[0:2] == 'C ':
		msg_parts = msg[2:].split(' ')
		node.node_connect(msg_parts[0], int(msg_parts[1]))
	elif msg[0:2] == 'T ':
		node.node_chat(myUsername: msg[2:])
	elif msg[0:2] == 'B ':
		node.node_broadcast_file(msg[2:])
	elif msg == 'G':
		node.node_get_files()
	elif msg[0:2] == 'R ':
		node.node_request_file(msg[2:])
node.node_close()
