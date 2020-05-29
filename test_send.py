import threading
from time import sleep

from MRTclass import MRT
import sys
import random

# test code
host = 'localhost'

port1 = int(sys.argv[1])
port2 = int(sys.argv[2])
# file = sys.argv[3]


if len(sys.argv) < 3:
    print("Usage: test_receiver.py conn_port")
    exit



udp = MRT()

try:
    connid = udp.mrt_connect(host, port2)
    print("ConnectId =", connid)

    # for i in chunks:

    for line in sys.stdin:

        udp.mrt_send(line, connid)

finally:
    udp.mrt_disconnect(connid)