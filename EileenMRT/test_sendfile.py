import sys
from time import sleep

from udpsender import UdpSender, SendFile
import consts as CONST

# test code
server_addr = ('localhost', 12345)

if len(sys.argv) < 2:
    print("Usage: test_sendfile.py filepath")
    exit

print("Input file path {}".format(sys.argv[1]))

ret = SendFile(server_addr, sys.argv[1])

print("Return value=", ret)
