# implements a STUN client that talks to STUN server using STUN protocol RFC5389
# returns NAT type, source ip and port, mapped ip and port, and changed ip and port

# https://www.linuxjournal.com/article/9004
# head node has information about each peer's mapped IP and Port address
# we tell the head node that we are listening at that public IP/port pair
# and request the P2P target node to initiate a request to us. Then, we can connect to it as a reply to that message.
# Hole punching: if both P2P nodes behind the NAT send packets to each other's public IP/port,
# the first packet from each party is discarded because it was unsolicited.
# But subsequent packets are let through because NAT thinks the packets are replies to our original request
# need headers in the packets to label if it's sending a reply meant for the P2P client or sending a request meant for the P2P server

# this won't work if both nodes are behind the same NAT device. So, first figure out whether we can communicate directly using the private IP address itself.
# special case if you run into brain-damaged NAT devices at both ends. In that situation, the only way is to make the rendezvous server act as a relay for the traffic.

# def connect (host, port): # mapped ip and port returned by stun
#     send RCON to private IP/port
#     if ACON received:
#         return
#     else:
#         tell head node to request RCON from target node
#         send RCON to target node's public mapped IP/port
#         send another RCON
#         receive ACON


import socket
import sys
import binascii
import random

# STUN message types
message_type = {
b'0001': 'BindRequest',
b'0101': 'BindResponse',
b'0111': 'BindErrorResponse',
b'0002': 'SharedSecretRequest',
b'0102': 'SharedSecretResponse',
b'0112': 'SharedSecretErrorResponse'}

# STUN attributes
MappedAddress = '0001'
ChangeRequest = '0003'
SourceAddress = '0004'
ChangedAddress = '0005'

# STUN [RFC3489] uses these terms for NAT type:
FullCone = 'Full Cone NAT'
RestrictedCone = "Restricted Cone NAT"
PortRestrictedCone = "Port Restricted Cone NAT"
Symmetric = 'Symmetric NAT'
NoConnect = "Could not connect to a STUN server"


# read IP and port info from Stun message as bytes and return string
def translate_ip_port(data, base):
    port = int(binascii.b2a_hex(data[base + 6:base + 8]), 16)
    ip = ".".join([str(int(binascii.b2a_hex(data[base + 8:base + 9]), 16)), str(int(binascii.b2a_hex(data[base + 9:base + 10]), 16)), str(int(binascii.b2a_hex(data[base + 10:base + 11]), 16)), str(int(binascii.b2a_hex(data[base + 11:base + 12]), 16))])
    return port, ip

# Sends data to STUN server and parses STUN message attributes
# from attributes, returns IP and PORT values
def get_values(sock, host, port, content=''):
    values = {'Response': False, 'SourceIP': None, 'SourcePort': None, 'MappedIP': None, 'MappedPort': None, 'ChangedIP': None, 'ChangedPort': None}
    test = ''.join(random.choice('0123456789ABCDEF') for i in range(32))
    str_data = ''.join(['0001', "%#04d" % (len(content)/2), test, content]) # Bind Request
    data = binascii.a2b_hex(str_data)

    recieved, correct = False, False
    msg, addr = None, None

    while not correct:
        while not recieved:
            try:
                sock.sendto(data, (host, port))
            except socket.gaierror:
                return values # response will still be false
            try:
                msg, addr = sock.recvfrom(1024)
                recieved = True # message was received
            except Exception:
                return values # response will still be false

        bindresponse, same_test = False, False

        if message_type[binascii.b2a_hex(msg[0:2])] == "BindResponse":
            bindresponse = True
        # if response received is the same as sent
        if bytes(test.upper().encode()) == binascii.b2a_hex(msg[4:20]).upper():
            same_test = True
        # the bind request is met with correct response
        if bindresponse and same_test:
            correct = True
            values['Response'] = True
            left = int(binascii.b2a_hex(msg[2:4]), 16) # there are bytes left to read
            base = 20
            while left:
                # parse attribute type and assign correct values
                attribute = binascii.b2a_hex(msg[base:(base + 2)])
                length = int(binascii.b2a_hex(msg[(base + 2):(base + 4)]), 16)

                if attribute == bytes(MappedAddress.encode()):
                    port, ip = translate_ip_port(msg, base)
                    values['MappedPort'], values['MappedIP'] = port, ip
                if attribute == bytes(SourceAddress.encode()):
                    port, ip = translate_ip_port(msg, base)
                    values['SourcePort'], values['SourceIP'] = port, ip
                if attribute == bytes(ChangedAddress.encode()):
                    port, ip = translate_ip_port(msg, base)
                    values['ChangedPort'], values['ChangedIP'] = port, ip
                base += 4 + length
                left -= 4 + length
    return values


# getting NAT type
def get_type(sock, sourceIP, stunServer, stunPort):

    values = get_values(sock, stunServer, stunPort)

    # no response means the client couldn't connect to the STUN server
    if not values['Response']:
        return NoConnect, values

    mapPort, mapIP, changedPort, changedIP = values['MappedPort'], values['MappedIP'], values['ChangedPort'], values['ChangedIP']

    if values['MappedIP'] != sourceIP:
        change = ''.join([ChangeRequest, '0004', "00000006"])
        values = get_values(sock, stunServer, stunPort, change)
        if values['Response']:
            type = FullCone # Open internet, means peer can send to ip and port
        else:
            values = get_values(sock, changedIP, changedPort)
            # ChangeRequest useful for determining whether the client is behind a restricted cone NAT or restricted port cone NAT.
            # They instruct the server to send the Binding Responses from a different source IP address and port.
            # source: https://www.3cx.com/blog/voip-howto/stun-details/
            if mapIP == values['MappedIP'] and mapPort == values['MappedPort']:
                values = get_values(sock, changedIP, stunPort, ''.join([ChangeRequest, '0004', "00000002"]))
                if values['Response']:
                    type = RestrictedCone
                else:
                    type = PortRestrictedCone
            else:
                type = Symmetric
    return type, values


# getting IP info
def main(sourceIP, sourcePort, stunServer, stunPort=3478):

    # set up the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(2)
    # sock.bind((sourceIP, sourcePort))
    sock.bind(('', sourcePort))

    # get nat type and ip/port values
    natType, values = get_type(sock, sourceIP, stunServer=stunServer, stunPort=stunPort)

    if natType == FullCone:
        print("Peer may connect to " + str(values['MappedIP']) + ":" + str(values['MappedPort']))
    elif natType == NoConnect:
        print("Could not connect to a STUN server")
    else:
        # other types are RestrictedCone, PortRestrictedCone, Symmetric
        print("I am " + str(values['MappedIP']) + ":" + str(values['MappedPort']) + ", but probably unreachable")

    sock.close()

    return natType, values


ip = socket.gethostname()
port = 54321
server = str(sys.argv[1])

print(main(ip, port, server))
