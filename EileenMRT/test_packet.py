from packet import Packet
import consts as CONST

# test Packet class methods: pack and unpack
fragNum = 0
myInput = ''
while myInput != 'quit':
    myInput = input()
    onePacket = Packet(0, 0, CONST.DATA, fragNum, 0, myInput)
    packed = onePacket.pack()
    print(packed)
    fragNum = fragNum + 1

    # let's unpack it
    newPacket = Packet()
    newPacket.unpack(packed)
    print('Unpacked is Valid? ', newPacket.isValid)

