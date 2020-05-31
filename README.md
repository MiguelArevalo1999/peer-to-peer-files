# Peer to Peer File Sharing
## COSC 60 Final Project, Group Anjer, 20S
Group members: Shane Hewitt, Brett Kidman, Eileen Xia, Sean Simons, Thomas Lingard, Elizabeth Wilson

## Description 
This project is an implementation of a peer to peer file sharing service. Each peer has both client and server capabilities, and acts as a floating vertex of a larger graph of nodes. The file sharing happens using an implementation of a mini reliable transport protocol implemented in lab 3, which has the capability to open to connections, accept one/all connections, broadcast a message, accept a file, connect, disconnect, and close itself. The broadcasting uses UDP and has a sliding window implementation to deal with dropped packets. When clients wish to form a connection, they broadcast their IP and the file that they are looking for, after which a client within their network who has that file will transfer it to them.

## Usage 
Run `python node_client.py`. You'll be prompted to enter a IP and a port. The first node to run at the port becomes the super node. 
- `C port #` to connect to the supernode at that port if it exists.
- `T your chat here` to chat with other nodes 
- `Q` to quit. If the supernode quits, the supernode status will be transported down the list of clients who have joined in order. 

## Testing 
Testing was done using the node_*.py files. These implemented the Node class and all performed different tests. Running these simultaneously on the same computer, different computers, and different wifis is how we tested our file sharing program. 

## Extras 
- The network tries to form connections between nodes (automatically) to increase the resilience of the network
When a node is opened, it searches at the IP and port that it was opened at for incoming connections. If it finds one, it will automatically connect. Also, when the supernode disconnects the node that joined the supernode first becomes the supernode and is passed the information of all the other nodes in the network. 

- Routes for exchanging files are efficient (this might be hard to test if you've already implemented option 1, so perhaps turn that into a switch)
The supernode holds the files that are being downloaded, so the furthest that a file will travel to be exchanged is between some node, the supernode, and the node that requested the file.

- Apart from downloading files, users can chat
Using the command `T ` followed by a message will send out your message preceeded by a username to anyone in your network. 