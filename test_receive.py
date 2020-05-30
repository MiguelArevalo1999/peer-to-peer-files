import threading
from time import sleep

from MRTclass import MRT
import sys
import random

# test code
host = 'localhost'

port1 = int(sys.argv[1])
# port2 = int(sys.argv[2])
# file = sys.argv[3]


if len(sys.argv) < 2:
    print("Usage: test_receiver.py myport")
    exit



udp = MRT()

if udp.mrt_open(host, port1):

    accepted_conn = []
    while True:

        accepted_conn.extend(udp.mrt_accept_all())
        for conn in accepted_conn:
            print("received connection from " + str(conn))
            data = udp.mrt_receive1(conn)
            print("received message " + data + " from " + str(conn))

        # data = udp.mrt_probe(accepted_conn)

    # while True:
    #
    #     accepted_conn = udp.mrt_accept_all()
    #     for conn in accepted_conn:
    #         print("received connection from " + str(conn))
    #         udp.mrt_receive1(conn)
    #         print("received message from " + str(conn))


udp.mrt_close() # stop receiving

