import struct
import hashlib
import time
import consts as CONST

# generate a 4-byte checksum for a string
def checksum(str):
    # csum = abs(hash(str)) % CONST.MAX_INT
    md5 = hashlib.md5()
    md5.update(str)
    digest = md5.hexdigest()
    csum = int(digest, 16) % CONST.MAX_INT
    # print('check sum for "{}" is {} '.format(str, csum))
    return csum

class Packet:
    def __init__(self, connId=0, checksum=0, type=CONST.DATA, fragNum=0, winAdv=0, payload=""):
        self.connId = connId
        self.checksum = checksum
        self.type = type
        self.fragNum = fragNum
        self.winAdv = winAdv
        self.payload = payload
        self.isValid = False

        self.timestamp = int(round(time.time() * 1000))

    def setPayload(self, payload):
        self.payload = payload
        self.isValid = True

    def resetTimestamp(self):
        self.timestamp = int(round(time.time() * 1000))

    # use struct to pack this packet
    def pack(self):
        # when the packet is being packed, we need to calculate its checksum
        b = self.payload.encode('utf-8')
        self.checksum = checksum(b)
        return struct.pack( (CONST.PACK_FMT+"%ds") % (len(b)), 
            self.connId, self.checksum, self.type, self.fragNum, self.winAdv, b)
    
    # unpack data into different fields, including payload
    def unpack(self, data):
        fldSz = struct.calcsize(CONST.PACK_FMT)
        if fldSz >= len(data):
            p = struct.unpack(CONST.PACK_FMT, data)
            csum = checksum(b"")
            self.payload = ""
        else:
            p = struct.unpack((CONST.PACK_FMT+"%ds") % (len(data) - fldSz), data)
            csum = checksum(p[5])
            self.payload = p[5].decode('utf-8')

        # for i in range(0, len(p)):
        #     print('unpacked field ', i, p[i])

        self.connId = p[0]
        self.checksum = p[1]
        self.type = p[2]
        self.fragNum = p[3]
        self.winAdv = p[4]
        
        # print("Unpack csum {}, frag# {}".format(self.checksum, self.fragNum))
        # let's compare the checksum
        # print("Received checksum {}, calc checksum {}".format(self.checksum, csum))
        self.isValid = (self.checksum == csum)


