import os 
import tempfile
import consts as CONST

# client message consists of Packet objects
# When final packet comes, we need to check for missing packets.
# If there're missing packets, we need to ask the client to re-send those packets
class ClientMessage:
    def __init__(self, client):
        self.msg = {}   # we use a dict for all packets received so far
                        # key is fragNum, and value is Packet
        self.total = 0
        self.startNum = 0
        self.tmpfilename = None
        self.tmpfileid = None

    # let's see we need to dump some packets if it's getting too big
    def dumpToFile(self):
        # find sequence of packets starting startNum, and count their size. 
        # print("Check if we need to dump to file")
        siz = 0
        packno = self.startNum
        while True:
            if packno in self.msg:
                siz += len(self.msg[packno].payload)
                packno += 1
            else:
                break
        
        if siz >= CONST.DUMP_SIZE_THRESHOLD:
            # print("dump to file from {} to {}".format(self.startNum, packno))
            if not self.tmpfilename:
                self.tmpfileid = tempfile.NamedTemporaryFile(mode="r+b", delete=False)
                self.tmpfilename = self.tmpfileid.name
            
            for i in range(self.startNum, packno):
                # print("Dump pack#", i)
                self.tmpfileid.write(self.msg[i].payload.encode('utf-8'))
                self.msg[i].payload = ""

            # fd.close()
            self.startNum = packno

    def addPacket(self, packet):
        if packet.fragNum in self.msg:
            pass
        else:
            self.msg.update({packet.fragNum: packet})
            self.dumpToFile()

    def checkMissingPackets(self, num):
        self.total = num
        missing = []
        for i in range(0, num):
            if not i in self.msg:
                 missing.append(i)

        return missing

    def constructMessage(self):
        if self.tmpfilename:
            if self.startNum < self.total:
                for i in range(self.startNum, self.total):
                    # print("Dump leftover pack#", i)
                    self.tmpfileid.write(self.msg[i].payload.encode('utf-8'))
                    self.msg[i].payload = ""

                self.tmpfileid.close()
            # all dumped to file
            filesize = os.path.getsize(self.tmpfilename)
            return filesize, "filename: " + self.tmpfilename
        else:
            txt = ""
            for i in range(0, self.total):
                txt += self.msg[i].payload

            size = len(txt)
            return size,txt

        
