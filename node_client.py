import sys
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import tkinter
sys.path.append('../')
from Node import Node

supernodo = Tk()
supernodo.title("SuperNodo")
supernodo.resizable(0,0)
supernodo.geometry("750x800")
supernodo.config(bg="black")

myFrame = Frame()
myFrame.config(bg="white")
myFrame.pack(side="top")

#Logo Cobra
imagen = tk.PhotoImage(file="cobra.png")
imagen_sub = imagen.subsample(20,20)
widget = tk.Label(image=imagen_sub)
widget.place(x=250,y=5)

#Label SuperNodos
label_supernodos = Label(supernodo,text="Super Nodos")
label_supernodos.place(x=10,y=120)

#Label Nodos
label_nodos = Label(supernodo,text="Nodos")
label_nodos.place(x=350,y=120)

#Frame supernodo
supernodo_frame = Frame(supernodo, bg='white', width=200, height=250, pady=3)
supernodo_frame.place(x=10,y=150)

# rows and columns as specified
ip_label = Label(supernodo_frame, text='IP')
ip_label.grid(row=1, column=0,padx=(0,50))
puerto_label = Label(supernodo_frame, text='Puerto')
puerto_label.grid(row=1, column=1,padx=(0, 50))
contador_label = Label(supernodo_frame, text='Contador')
contador_label.grid(row=1, column=2,padx=(0, 50))

#Frame nodo
nodo_frame = Frame(supernodo, bg='white', width=200, height=250, pady=3)
nodo_frame.place(x=350,y=150)

# rows and columns as specified
ip_label = Label(nodo_frame, text='IP')
ip_label.grid(row=1, column=0,padx=(0, 50))
puerto_label = Label(nodo_frame, text='Puerto')
puerto_label.grid(row=1, column=1,padx=(0, 50))
contador_label = Label(nodo_frame, text='Contador')
contador_label.grid(row=1, column=2,padx=(0, 50))

#Frame archivos
archivos_frame = Frame(supernodo, bg='white', width=200, height=250, pady=3)
archivos_frame.place(x=10,y=480)

#Label Archivos
label_archivos = Label(supernodo,text="Archivos")
label_archivos.place(x=10,y=450)

# rows and columns as specified
nombre_label = Label(archivos_frame, text='Nombre')
nombre_label.grid(row=1, column=0,padx=(0, 100))
md5_label = Label(archivos_frame, text='MD5')
md5_label.grid(row=1, column=2,padx=(0, 100))
ubicacion_label = Label(archivos_frame, text='Ubicacion')
ubicacion_label.grid(row=1, column=4,padx=(0, 100))

node = Node()

# print('Will you be connecting to / accepting nodes on different networks? (Y/N)')
# YorN = input('')
# if YorN == 'Y':
# 	overWifi = True
# elif YorN == 'N':
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
supernodo.mainloop()