import secrets # NOTE: Secrets library requires Python 3.6 or above
import struct
import binascii
from enum import Enum
import socket
import sys

class MessageTypes(Enum):
  REQUEST = 1
  INDICATION = 2
  SUCCESS = 3
  ERROR = 4

server1addr = 'stun.stunprotocol.org'
server1port = 3478

MAGIC_COOKIE = 0x2112a442
MAPPED_ADDRESS = 0x0001
CHANGED_ADDRESS = 0x0005
USERNAME = 0x0006
XOR_MAPPED_ADDRESS = 0x0020

# From RFC 5380
CHANGE_REQUEST = 0x0003
PADDING = 0x0026
RESPONSE_PORT = 0x0027
RESPONSE_ORIGIN = 0x802b
OTHER_ADDRESS = 0x802c

#Flags for Change Request
CHANGE_NONE = 0x00000000
CHANGE_PORT = 0x00000002
CHANGE_IP = 0x00000004
CHANGE_BOTH = 0x00000006

# RFC 5389 section 6 indicates the 96-bit transaction id should be
# cryptographically random


def make_transaction_id():
  return secrets.token_bytes(12)


def make_message_type(mt):
  if mt == MessageTypes.REQUEST:
    return 0x0001
  elif mt == MessageType.INDICATION:
    return 0x0011
  elif mt == MessageType.SUCCESS:
    return 0x0101
  elif mt == MessageType.ERROR:
    return 0x0111

def make_change_request(flag):
  flag_value = flag.to_bytes(4, 'big')
  return CHANGE_REQUEST.to_bytes(2, byteorder='big') + len(flag_value).to_bytes(2, 'big') + flag_value

def parse_mapped_address(attr_val):
  ipv = ''
  if attr_val[1] == 1:
    ipv = 'IPV4'
  if attr_val[1] == 2:
    ipv = 'IPV6'
  port_num = attr_val[2:4]
  port_num = port_num[0]*256 + port_num[1]
  IP_addr = attr_val[4:]
  return ipv, IP_addr, port_num
  print("{0:d}.{1:d}.{2:d}.{3:d}:{4:d}".format(IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num))

def parse_response_origin(attr_val):
  return parse_mapped_address(attr_val)

#RFC 5780: informs the client of the source IP address and port that would be used if the client requested the "change IP" and "change port" behavior.
def parse_other_address(attr_val):
  return parse_mapped_address(attr_val)

def parse_xor_mapped_address(attr_val):
  ipv = ''
  if attr_val[1] == 1:
    ipv = 'IPV4'
  if attr_val[1] == 2:
    ipv = 'IPV6'
  xor_magic_cookie = MAGIC_COOKIE.to_bytes(4, byteorder = 'big')
  port_num = attr_val[2:4]
  port_num_new = [0,0]
  for x in range(0,1):
    port_num_new[x] = port_num[x]^xor_magic_cookie[x]
  port_num = port_num_new[0]*256 + port_num_new[1]
  IP_addr = attr_val[4:]
  IP_addr_new = [0,0,0,0]
  for x in range(0,3):
    IP_addr_new[x] = IP_addr[x]^xor_magic_cookie[x]
  IP_addr = IP_addr_new
  return ipv, IP_addr, port_num
  print("{0:d}.{1:d}.{2:d}.{3:d}:{4:d}".format(IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num))

def compile_message(mt, txid, attr):
  if not attr:
    return mt.to_bytes(2, byteorder='big') + 0x0000.to_bytes(2, byteorder='big') + MAGIC_COOKIE.to_bytes(4, byteorder='big') + txid
  else:
    return mt.to_bytes(2, byteorder='big') + len(attr).to_bytes(2, byteorder='big') + MAGIC_COOKIE.to_bytes(4, byteorder='big') + txid + attr

def handle_response(response,msg):
  rmt = response[0:2]
  rmt = (rmt[0]*256) + rmt[1]
  rlen = response[2:4]
  rlen = (rlen[0]*256) + rlen[1]
  rcookie = response[4:8]
  rtxid = response[8:20]
  if rmt == 0x0111 or rmt == 0x0110:
    print("STUN Server responded with error.")
    return False
  elif rcookie != MAGIC_COOKIE.to_bytes(4, byteorder='big'):
    print('Magic cookie is not expected value.')
    return False
  elif rtxid != msg[8:20]:
    print('transaction id does not match.')
    return False
  #if rmt == 0x0101:
  #  print('Success!')

  myip = ''
  myport = ''
  otherdestip = ''
  otherdestport = ''

  ptr = 20
  while ptr - 20 < rlen:
    attrtype = response[ptr:ptr+2]
    attrtype = attrtype[0]*256 + attrtype[1]
    attrlen = response[ptr+2:ptr+4]
    attrlen = (attrlen[0]*256) + attrlen[1]
    attrvalue = response[ptr+4:ptr+4+attrlen]
    if attrtype == MAPPED_ADDRESS:
      ipv, IP_addr, port_num = parse_mapped_address(attrvalue)
      #print('Mapped Address. IP Version: {0}. IP Address: {1:d}.{2:d}.{3:d}.{4:d} Port: {5:d}'
      #  .format(ipv, IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num))
      myip = '{0:d}.{1:d}.{2:d}.{3:d}'.format(IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3])
      myport = port_num
    elif attrtype == RESPONSE_ORIGIN:
      ipv, IP_addr, port_num = parse_response_origin(attrvalue)
      #print('Response Origin. IP Version: {0}. IP Address: {1:d}.{2:d}.{3:d}.{4:d} Port: {5:d}'
      #  .format(ipv, IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num))
    elif attrtype == OTHER_ADDRESS:
      ipv, IP_addr, port_num = parse_other_address(attrvalue)
      #print('Response Other Address. IP Version: {0}. IP Address: {1:d}.{2:d}.{3:d}.{4:d} Port: {5:d}'
      #  .format(ipv, IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num))
      otherdestip = '{0:d}.{1:d}.{2:d}.{3:d}'.format(IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3])
      otherdestport = port_num
    elif attrtype == XOR_MAPPED_ADDRESS:
      ipv, IP_addr, port_num = parse_xor_mapped_address(attrvalue)
      #print('XOR Mapped Address. IP Version: {0}. IP Address: {1:d}.{2:d}.{3:d}.{4:d} Port: {5:d}'
      #  .format(ipv, IP_addr[0], IP_addr[1], IP_addr[2], IP_addr[3], port_num)) 
    ptr += 4+attrlen

  return myip, myport, otherdestip, otherdestport


def get_info(my_port_num):
  message = compile_message(make_message_type(
    MessageTypes.REQUEST), make_transaction_id(), ())

  message2 = compile_message(make_message_type(
    MessageTypes.REQUEST), make_transaction_id(), (make_change_request(CHANGE_BOTH)))

  message3 = compile_message(make_message_type(
    MessageTypes.REQUEST), make_transaction_id(), (make_change_request(CHANGE_PORT)))

  # SOCKET DGRAM
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind(('', my_port_num))
  connection = (server1addr, server1port)
  s.settimeout(2)
  s.sendto(message, connection)
  try:
    response, addr = s.recvfrom(1024)
  except:
    #print('Cant connect to STUN server')
    raise

  myip, myport, otherdestip, otherdestport = handle_response(response, message)

  if myip == socket.gethostbyname(socket.gethostname()):
    #print('Not behind a NAT')
    pass
  else:
    s.sendto(message2, connection)
    try:
      response, addr = s.recvfrom(1024)
    except:
      pass
    if response and response[0:2] != 0x0111:
      #print('Behind a Full-Cone NAT')
      pass
    else:
      s.sendto(message3, connection)
      try:
        response, addr = s.recvfrom(1024)
      except:
        pass
      if response and response[0:2] != 0x0111:
        #print('Behind a Restricted-Cone NAT')
        pass
      else:
        #print('Behind a Port Restricted Cone NAT')
        pass
  s.close()

  return myip, myport

#ip, port = get_info(8080)
#print(ip + ' ' + str(port))
# From RFC 3489 5. NAT Variations
#   Full Cone: A full cone NAT is one where all requests from the
#       same internal IP address and port are mapped to the same external
#       IP address and port.  Furthermore, any external host can send a
#       packet to the internal host, by sending a packet to the mapped
#       external address.

#    Restricted Cone: A restricted cone NAT is one where all requests
#       from the same internal IP address and port are mapped to the same
#       external IP address and port.  Unlike a full cone NAT, an external
#       host (with IP address X) can send a packet to the internal host
#       only if the internal host had previously sent a packet to IP
#       address X.

#    Port Restricted Cone: A port restricted cone NAT is like a
#       restricted cone NAT, but the restriction includes port numbers.
#       Specifically, an external host can send a packet, with source IP
#       address X and source port P, to the internal host only if the
#       internal host had previously sent a packet to IP address X and
#       port P.



