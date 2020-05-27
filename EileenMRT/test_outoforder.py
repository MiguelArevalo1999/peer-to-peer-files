from time import sleep
from udpsender import UdpSender, SendFile
import consts as CONST

# test code
server_addr = ('localhost', 12345)

msgTemplate = "message #{} "
# msgSeq = [1, 0, 3, 2]
msgSeq = [1, 0, 3, 2, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17, 18, 19, 20, 21, 22, 25, 24, 23, 12, 13, 14, 4]


udp = UdpSender(server_addr)

try:
    connid = udp.mrt_connect()
    print("ConnectId =", connid)
    for msgid in msgSeq:
        rettype, svraddr = udp.mrt_send(msgid, CONST.DATA, msgTemplate.format(msgid))
        sleep(0.1)  # delay 100ms

    #delay 500ms
    sleep(0.5)

    # send the final packet
    rettype, svraddr = udp.mrt_send(len(msgSeq), CONST.RCLS)

finally:
    udp.mrt_disconnect()


