# Peer to Peer File Sharing
## COSC 60 Final Project, Group Anjer, 20S
Group members: Shane Hewitt, Brett Kidman, Eileen Xia, Sean Simons, Thomas Lingard, Elizabeth Wilson

## Description 
This project is an implementation of a peer to peer file sharing service. Each peer has both client and server capabilities, however only one peer acts as a server and becomes a "super node."  Every other client, or node, connects to this super node and messages between nodes are forwarded through the super node.  This network utilizes UDP to send packets and implements a sliding window to deal with dropped packets. In order to connect between routers behind NAT's, we utilize the `STUN\_library.py` file to determine the public port and IP address to use when connecting between NAT protected routers.  The protocol used is built around the mini reliable transport layer, or MRT for short, protocol.  All the functions necessary for MRT are stored in the `MRT.py` file.  Every client stores necessary information in its own `Node` class with functions that call the necessary MRT functions.  These node functions are stored in the `Node.py` file.  The primary MRT functions are:
1.  `mrt\_open`:  This signals that a node is ready to receive connections from other nodes.
2.  `mrt\_connect`:  This initiates a two way connection between the super node and the connecting node.  The two way connection is necessary for UDP communication between routers behind NAT's.
3.  `mrt\_accept\_all`/`mrt\_accetp1`:  These functions accept pending connections that are waiting to connect, where `accept1` accepts a single pending connection and `accept\_all` accepts all the pending connections.
4.   `mrt\_broadcast`:  This allows for a node to signal all other nodes of a message.  We have used this to implement chatting on the network.
5.  `mrt\_broadcast\_file`:  This allows for a node to broadcast the name of a file that they have available for other nodes to download. 
6.  `mrt\_receive1`:  This function will receive data over a single connection when there is at least a byte of data on the connection.
7.  `receive\_file`:  A function which will create and write a file with the same content as the requested file.
8.   `request\_file`:  A function which sends a request message to all nodes to download the specified file.
9.  `send\_peers`:  
10.  `update\_peers`:
11.  `migrate\_host`:
12.  `mrt\_send`:  A function which sends some data over a specific connection and has some blocking capabilities.  
13.  `get\_files`:  A function which will return a list of the files available for download on a network, regardless of which node has it.
14.  `receive\_ack`:  A threaded function that makes it able for a client to receive acknowledgment packets while sending more data.  
15.  `receiver_receive`:  A threaded function that continually runs in the background and receives any packet for a client, parses the message, and calls necessary functions depending on the packet.
16.  `add\_checksum`/`verify\_checksum`:  These functions add or verify a checksum to packets which are based on the message, which helps detect malicious packet manipulation.
The primary node functions are:
1.  `node\_open`:  This initiates a client node and allows for other nodes to connect to the new client node.  It also starts a thread which constantly runs and checks for any new connections and accepts them all.
2.  `node\_accept`:  This function constatnly runs while a node remains open and will accept any pending connection that has been requested.
3.  `node\_invite`:
4.  `node\_connect`:  This function will automatically try and connect to the given IP and port.
5.  `node\_chat`:  This function will send out a public message between all nodes.
6.  `node\_broadcast\_file`:  This function allows for a node to broadcast a file available for download to all other nodes in the network.
7.  `node\_get_\_files`:  This functions requests a list of files available for download from all the other nodes.
8.  `node\_request\_file`:  A function to download a certain file on the network.
9.  `node\_close`:  A function to signal that a node is no longer accepting connections and disconnects it from the network.
## Usage 
This code was built using Python 3.  Please ensure that Python 3 is installed on your computer.  To begin using a client run `python3 node\_client.py` from the given directory.  You'll be prompted to enter a IP and port, please use your local IP and any port.  If you don't know your local IP, simply hit enter when the IP prompt appears.  This will automatically fill in the local IP under the hood.  After you have entered both of these you can enter the commands below. 
1.  `C <public IP> <public port>`:  This command tries to connect a node.  Please note that in order to connect to another node, you must give the public ip and port number that might change depending on their NAT.  Also, a two-way connection is needed to connect two nodes due to some NAT types, meaning that both nodes must call this command on each other to to connect to the supernode at that port if it exists.  A confirmation message will appear on a successful connection.
2.  `T <chat message>`:  This command will send the typed message to all other nodes in the network.
3.  `I`:
4.  `B <file name>`:  This command will broadcast the file name you have availabe to download to all other nodes in the network.  Please note that the file must be in same directory as the programs files describes above.
5.  `G`:  This command will list all the files currently availabe to download in the network. 
6.  `R <file name>`:  This command will download the given file name, if it is available on the network, and save it to the directory where these program files are.  
7.  `Q` to quit. If the supernode quits, the supernode status will be transported down the list of clients who have joined in order. 
