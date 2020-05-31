# Protocol:
# 2 peers A and B, both connected to headnode S
# 1) A asks S for help establishing UDP session with B
# 2) S replies to A with message containing B's public and private addresses
# 3) at the same time, S sends B a connections request message with A's public and private addresses
# 4) A receives B's addresses and starts sending UDP packets to both endpoints. Locks in whichever endpoint elicits a valid response
# 5) Simultaneously, B send UDP packets to both of A's known endpoints and locks in the first endpoint that works

# The headnode might obtain the client's private endpoint from the client itself in a field in the body of the client's registration message,
# and obtain the client's public endpoint from the source IP and port fields in the headers of that registration message.
# If the client is not behind a NAT, then its private and public endpoints should be identical.

import socket
import _thread

# node = Node()
# node.node_open('127.0.0.1', 8080)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 8080

server.bind((host, port))
server.listen(5)
addresses = []

def newclient(conn):

    while True:
        try:
            message = conn.recv(2048).decode("utf-8")
            message = message.replace("\n", "")
            print(message)
            if message == "RCON":
                print("server - send client info to: %s", addresses[0]) # send B's info to A
                # msg = '{}:{}'.format(addresses[1][0], str(addresses[1][1])).encode('utf-8')
                conn.sendto(msg, addresses[0])
                print("server - send client info to: %s", addresses[1]) # send A's info to B
                msg = '{}:{}'.format(addresses[0][0], str(addresses[0][1])).encode('utf-8')
                conn.sendto(msg, addresses[1])
                addresses.pop(1)
                addresses.pop(0)

            else:
                break
        except:
            continue



while True:
    #establish connection
    print("Server binded to {0}. Now ready to receive connections...".format((host, port)))
    conn, addr = server.accept()
    addresses.append(conn)

    print(addr[0] + " connected. User number " + str(len(addresses)))

    # create thread for each new  connection
    _thread.start_new_thread(newclient,(conn,))

conn.close()
server.close()



# import socket
# import sys
#
#
# if len(sys.argv) < 2:
#     print("Usage: stun_receiver.py port")
#
# host='127.0.0.1'
# port = int(sys.argv[1])
#
# addresses = []
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
# sock.bind((host, port))
#
# while True:
#     data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#     print("connection from: %s", addr)
#     addresses.append(addr)
#     if len(addresses) >= 2:
#         print("server - send client info to: %s", addresses[0])
#         msg = '{}:{}'.format(addresses[1][0], str(addresses[1][1])).encode('utf-8')
#         sock.sendto(msg, addresses[0])
#         print("server - send client info to: %s", addresses[1])
#         msg = '{}:{}'.format(addresses[0][0], str(addresses[0][1])).encode('utf-8')
#         sock.sendto(msg, addresses[1])
#         addresses.pop(1)
#         addresses.pop(0)



