import sys
import tkinter as tk

sys.path.append('../')
from Node import Node

node = Node()
print('Will you be connecting to / accepting nodes on different networks? (Y/N)')
YorN = input('')
if YorN == 'Y':
	overWifi = True
elif YorN == 'N':
	overWifi = False
print('Enter IP')
myip = input('')
print('Enter Port')
myport = int(input(''))
print('Please Enter a Display Name for chat features.')
myuser = input('')

print('\n')
print('COMMANDS')
print('---------------------------------------------------------')
print('C [Target IP] [Target Port] | Attempts to connect to target node.')
print('A [Target IP] [Target Port] | Used by supernode to allow target node to connect to the network.')
print('T [message] | Chat functionality, sends chat message to all other nodes in network.')
print('B [file name] | Broadcasts a file to network and makes available for download. File must be in current directory.')
print('G | prints a list of all previously broadcasted files.')
print('R [file name] | Request / download a broadcasted file.')
print('Q | Disconnect from the network and quit the program.')
print('\n')

node.node_open(myip, myport, overWifi)
while True:
	msg = input('')
	if msg == 'Q':
		break
	elif msg[0:2] == 'C ': # Connect to another node
		msg_parts = msg[2:].split(' ')
		node.node_connect(msg_parts[0], int(msg_parts[1]))
	elif msg[0:2] == 'A ': # Used by supernode to accept incoming connection (just sends empty packets to traverse NAT and allow RCON/ACON protocol to work)
		msg_parts = msg[2:].split(' ')
		node.node_invite(msg_parts[0], int(msg_parts[1]))
	elif msg[0:2] == 'T ': # "Talk", chat functionality.
		node.node_chat('{0}: {1}'.format(myuser, msg[2:]))
	elif msg[0:2] == 'B ': #broadcasts a file and makes available for download
		node.node_broadcast_file(msg[2:])
	elif msg == 'G': #get a list of all broadcasted files.
		node.node_get_files()
	elif msg[0:2] == 'R ': #Request, downloads a broadcasted file.
		node.node_request_file(msg[2:])
node.node_close()