import sys
from udpsender import UdpSender, SendFile
import consts as CONST
from time import sleep
import random


PACKET_SIZE = 1500

server_addr = ('localhost', 12345)


if len(sys.argv) < 2:
    print("Usage: test_sender.py delay")
    exit

# def split_into_chunks(data, pack_size=PACKET_SIZE):
#     if (len(data) < pack_size):
#         chunks = []
#         chunks.append(data)
#     else:
#         chunks = [(data[i:i + pack_size]) for i in range(0, len(data), pack_size)]
#
#     return chunks
# text = ""
# for line in sys.stdin:
#     text += line
# chunks = split_into_chunks(text)

udp = UdpSender(server_addr)
# udp.setRandomTest(True) #randomly generates delay

delay = sys.argv[1] == "True"

random.seed(13)

fragnum = 0
try:
    connid = udp.mrt_connect()
    print("ConnectId =", connid)

    # for i in chunks:

    for line in sys.stdin:

        rettype, svraddr = udp.mrt_send(fragnum, CONST.DATA, line)
        fragnum += 1

        if delay:
            # create random delay
            sleep(5*random.random())

    # send the final packet
    # print("To close fragnum ", fragnum)
    rettype, svraddr = udp.mrt_send(fragnum, CONST.RCLS)

finally:
    udp.mrt_disconnect()
