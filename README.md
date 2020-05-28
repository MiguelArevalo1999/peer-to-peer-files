# Peer to Peer File Sharing
## COSC 60 Final Project, Group Anjer, 20S
Group members: Shane Hewitt, Brett Kidman, Eileen Xia, Sean Simons, Thomas Lingard, Elizabeth Wilson

## Description 
This project is an implementation of a peer to peer file sharing service. Each peer has both client and server capabilities, and acts as a floating vertex of a larger graph of nodes. The file sharing happens using an implementation of a mini reliable transport protocol implemented in lab 3, which has the capability to open to connections, accept one/all connections, broadcast a message, accept a file, connect, disconnect, and close itself. The broadcasting uses UDP and has a sliding window implementation to deal with dropped packets. When clients wish to form a connection, they broadcast their IP and the file that they are looking for, after which a client within their network who has that file will transfer it to them. 

## Usage 

## Testing 
