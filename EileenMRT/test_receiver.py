import threading
from time import sleep

from udpreceiver import UdpReceiver, ack_thread
import sys
import random

# test code
server_addr = ('localhost', 12345)

if len(sys.argv) < 4:
    print("Usage: test_receiver.py datacorrupt packetloss delay")
    exit

udp = UdpReceiver(server_addr, 10)

udp.setDataCorrupt(sys.argv[1] == "True")
udp.setPacketLoss(sys.argv[2] == "True")
delay = sys.argv[3] == "True"

random.seed(13)

if udp.mrt_open():
    try:
        x = threading.Thread(target=ack_thread, args=(udp,))
        x.start()
    except:
        print('Unable to start acknowledgement thread')

    while True:
        udp.mrt_accept1()

        # testing use of mrt_acceptall()

        # while True:
        #     connids = udp.mrt_accept_all()
        #     # print("Connections ", connids)
        #     if len(connids) == 0:
        #         # print("No new connection, sleep 1s")
        #         sleep(1)

        udp.mrt_receive1()

        if delay:
            sleep(5 * random.random())

        # testing use of probe
        # udp.mrt_probe()

udp.mrt_close()