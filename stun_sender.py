from Node import Node
import sys
import socket


# node = Node()
# port = int(sys.argv[1])
# node.node_open('127.0.0.1', port)
# node.node_connect('127.0.0.1', 8080)

host='127.0.0.1'
# port = int(sys.argv[1])
port = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
# sock.connect((host, port))
sock.sendto(b'0', (host, port))



while True:
    message = sys.stdin.readline()
    sock.sendto(str.encode(message), ('127.0.0.1', 8080))

    if message == "RCON\n":
        data, addr = sock.recvfrom(1024)
        print('client received: {} {}'.format(addr, data)) # client received peer's address info
        ip, port = data.decode('utf-8').strip().split(':')
        addr = ip, int(port)
        sock.sendto(b'0', addr) # client sends to received address
        data, addr = sock.recvfrom(1024)
        print('client received: {} {}'.format(addr, data))

node.s.close()





#
#
# import socket
# import sys
#
# if len(sys.argv) < 2:
#     print("Usage: stun_receiver.py port")
#
# host='127.0.0.1'
# port = int(sys.argv[1])
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
# sock.sendto(b'0', (host, port))
#
# while True:
#     data, addr = sock.recvfrom(1024)
#     print('client received: {} {}'.format(addr, data))
#     ip, port = data.decode('utf-8').strip().split(':')
#     addr = ip, int(port)
#     sock.sendto(b'0', addr)
#     data, addr = sock.recvfrom(1024)
#     print('client received: {} {}'.format(addr, data))
#
#
#
