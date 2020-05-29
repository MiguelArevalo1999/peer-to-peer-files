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

    while True:

        conn = udp.mrt_accept1()
        print("received connection from " + str(conn))
        udp.mrt_receive1(conn)
        print("received message from " + str(conn))


udp.mrt_close() # stop receiving

