import socket
import errno
import os
import hashlib
import threading
import time
import random  # use to test "artificially" dropped packets


# MRT - Mini Reliable Transport

class MRT:
    BLOCKSIZE = 1024
    WINDOWSIZE = 10
    PACKETSIZE = 512
    TIMEOUT = .3  # How long the sender waits to receive an ACK before assuming the packet was lost

    connections = []  # contains all accepted connections
    connections_waitlist = []  # contains all connection requests not yet accepted.
    MAX_CONNECTIONS = 100  # max number of senders that can be connected to a receiver at any given time
    peers = []

    receiver_window = {}  # window that holds msg for each connection. Because of GBN implementation, receiver window holds only 1 msg at a time.
    expected_seq_num = {}  # keeps track of the expected sequence number for each connection
    seq_num = 0

    lock = threading.Lock()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ready = False
    connection_accepted = False
    receiver_thread = None
    directory = ''
    network_files = dict()

    def __init__(self):
        self.ready = False
        self.connection_accepted = False
        self.receiver_thread = threading.Thread(target=self.receiver_receive)

    def mrt_open(self, host, port):
        try:
            self.s.bind((host, port))
            self.ready = True
            self.receiver_thread.start()
            print("Server binded to {0}. Now ready to receive connections...".format((host, port)))
            return True
        except:
            raise
            print("Unable to bind server.")
            return False

    def mrt_connect(self, host, port):
        self.s.setblocking(False)
        self.connection_accepted = False
        while True:
            conn = (host, port)
            packet = add_checksum('RCON')
            self.s.sendto(packet, conn)
            #print('reached.')
            time.sleep(1)
            if self.connection_accepted == True:
                self.connections.append(conn)
                print("Connecting to {0}".format(conn))
                self.connection_accepted = False
                return conn

    def mrt_accept1(self):
        if not self.ready:
            return False
        while True:
            if self.connections_waitlist and len(
                    self.connections) < self.MAX_CONNECTIONS:  # if waitlist not empty and current number of connections doesnt exceed capacity
                self.lock.acquire()
                conn = self.connections_waitlist.pop(0)
                self.connections.append(conn)
                self.receiver_window[conn] = []
                self.expected_seq_num[conn] = 0
                print("Accepted connection from {0}".format(self.connections[-1]))
                self.lock.release()
                packet = add_checksum('ACON')
                self.s.sendto(packet, conn)
                # send connections list to all peers
                self.send_peers()
                return self.connections[-1]
            else:
                time.sleep(1)

    def mrt_accept_all(self):
        if not self.ready:
            return ()
        accepted_connections = []
        for conn in self.connections_waitlist:
            if len(self.connections) < self.MAX_CONNECTIONS:
                self.lock.acquire()
                conn = self.connections_waitlist.pop(0)
                self.connections.append(conn)
                self.receiver_window[conn] = []
                self.expected_seq_num[conn] = 0
                self.lock.release()
                accepted_connections.append(conn)
                print("Accepted connection from {0}".format(self.connections[-1]))
                packet = add_checksum('ACON')
                self.s.sendto(packet, conn)
                self.send_peers()
        return accepted_connections

    def mrt_receive1(self, conn):
        while conn in self.connections:  # blocks until there is data to return, unless the given connection disconnects.
            if len(self.receiver_window[conn]) == 1:
                self.lock.acquire()
                data = self.receiver_window[conn].pop()
                self.lock.release()
                return data
            time.sleep(.005)
        return ''

    def mrt_close(self):
        self.ready = False
        self.receiver_thread.join()
        print("no longer accepting connections.")
        return True

    def mrt_probe(self, connections):
        for conn in connections:
            if len(self.receiver_window[conn]) == 1:
                return conn
        return False

    def mrt_disconnect(self, conn):
        packet = add_checksum('RCLS')
        self.s.sendto(packet, conn)
        self.connections.remove(conn)
        print('Disconnected.')
        self.s.close()

    def mrt_send(self, data, conn):
        # seq_num = 0
        global ACKed_pack_num  # the index of the most recently ACKed packet. Can assume all packets before this have successfully been received. Beginning index of sliding window.
        global thread_flag  # used to stop thread
        global timeout_timer  # stopwatch to keep track of time since last ACK. If timeout, presume packet is dropped.
        ACKed_pack_num = 0
        thread_flag = True
        current_pack = 0  # index of packet to be sent
        packets = []
        while len(data) > 0:
            payload = data[0:self.PACKETSIZE - 12]
            data = data[self.PACKETSIZE - 12:]
            packet = "{0}{1:04d}{2}".format('DATA', self.seq_num, payload)
            packets.append(add_checksum(packet))
            self.seq_num += 1

        # thread to receive ACKs
        ACK_receipt = threading.Thread(target=self.receive_ACK)
        ACK_receipt.start()

        self.lock.acquire()
        timeout_timer = -1
        self.lock.release()

        while ACKed_pack_num < len(packets):  # as long as any packets remaining that have not yet been ACKed
            self.lock.acquire()
            while current_pack - ACKed_pack_num < self.WINDOWSIZE:  # number of unacknowledged packets in transit should not exceed window size
                try:
                    self.s.sendto(packets[current_pack],
                                  conn)  # When I tested against packet loss, I used randomint w/ if statement so 1/5 packets would be artificially "dropped" (would simply not sendto)
                except IndexError:  # cases where window size is greater than number of packets required
                    pass
                current_pack += 1

            if timeout_timer == -1:
                timeout_timer = time.time()  # start timer

            self.lock.release()
            time.sleep(.100)  # Allow time to receive more ACKS
            # Set a timer to keep track of time elapsed since last received an ACK. If timer exceeds TIMEOUT, consider packet dropped, go back to first index of window.
            if (time.time() - timeout_timer > self.TIMEOUT):
                self.lock.acquire()
                current_pack = ACKed_pack_num
                timeout_timer = -1  # stop timer
                print("Timeout. Packet dropped.")
                self.lock.release()

        # self.s.sendto(add_checksum('FINI'), conn) #send FINI packet to let receiver know that message is finished.
        thread_flag = False
        ACK_receipt.join()
        return True

    def mrt_chat(self, msg):
        msg_to_broadcast = "{0}{1}".format('CHAT', msg)
        packet = add_checksum(msg_to_broadcast)
        for conn in self.connections:
            self.s.sendto(packet, conn)

    def mrt_broadcast(self, conn, file):
        self.network_files[file] = conn[0]
        print(self.network_files)
        msg = '{0}{1}'.format('BCST', file)
        packet = add_checksum(msg)
        self.s.sendto(packet, conn)
        time.sleep(1)



    # def migrate_host(self)

    def send_peers(self):
        peers_list = ''
        for peer in self.connections:
            peers_list = peers_list + peer[0] + ':' + str(peer[1]) + ','
        peers_msg = add_checksum('PEER' + peers_list)
        for conn in self.connections:
            self.s.sendto(peers_msg, conn)

    def update_peers(self, peers_data):
        updated_peers = []
        peers_data = peers_data.split(',')[:-1]
        for peer in peers_data:
            peers_data = peer.split(':')
            connection = ()

    def receive_ACK(self):  # function so client can receive ACKs while sending data
        global ACKed_pack_num
        global thread_flag
        self.s.setblocking(False)

        while thread_flag:
            try:
                data, addr = self.s.recvfrom(self.BLOCKSIZE)
                data = data.decode()
                ACK = -1
                if data[8:12] == 'ADAT' and verify_checksum(data):
                    ACK = int(data[12:16])
                    print("Packet {0} acknowledged by receiver.".format(ACK))

                if (ACK >= ACKed_pack_num):
                    self.lock.acquire()
                    ACKed_pack_num = ACK + 1
                    timeout_timer = -1  # stop timer
                    self.lock.release()
            except socket.error as e:
                if e.errno == 10035:
                    pass
            time.sleep(.005)

    def receiver_receive(self):  # helper function for receiver to handle all incoming packets
        while self.ready:
            try:
                data, addr = self.s.recvfrom(self.BLOCKSIZE)
                data = data.decode()
                packet_type = data[8:12]
                if verify_checksum(data):
                    if addr not in self.connections:  # if data not from connected sender, check if requesting connection
                        if packet_type == 'RCON' and addr not in self.connections_waitlist:
                            self.connections_waitlist.append(addr)
                        elif packet_type == 'ACON':
                            self.connection_accepted = True
                    else:  # if data coming from a connected sender
                        if packet_type == 'DATA':
                            if int(data[12:16]) == self.expected_seq_num[addr] and len(
                                    self.receiver_window[addr]) == 0:  # and checksum check is true
                                self.lock.acquire()
                                self.receiver_window[addr].append(data[16:])  # add payload to receiver window
                                self.expected_seq_num[addr] += 1
                                self.lock.release()
                                packet = "{0}{1}".format('ADAT', data[12:16])
                                packet = add_checksum(packet)
                                self.s.sendto(packet, addr)
                        elif packet_type == 'RCLS':
                            self.lock.acquire()
                            self.connections.remove(addr)
                            self.receiver_window.pop(addr)
                            self.expected_seq_num.pop(addr)
                            self.lock.release()
                            print('{0} has disconnected.'.format(addr))
                            # send connections to all peers
                            self.send_peers()
                        elif packet_type == 'CHAT':
                            broadcasted_msg = data[12:]
                            print(broadcasted_msg)
                            for other_conn in self.connections:
                                if other_conn != addr:
                                    self.s.sendto(data.encode(), other_conn)
                        elif packet_type == 'PEER':
                            peers_list = data[12:]
                        # update peers
                        elif packet_type == 'BCST':
                            self.lock.acquire()
                            file = data[12:]
                            if file != '':
                                if file not in self.network_files:
                                    self.network_files[file] = addr
                                    for other_conn in self.connections:
                                        if other_conn != addr:
                                            self.s.sendto(data.encode(), other_conn)
                            print(self.network_files)
                            self.lock.release()
            except socket.error as e:
                if e.errno == 10035:
                    pass
            time.sleep(.005)


### HELPER FUNCTIONS ###
def verify_checksum(data):
    received_checksum = hashlib.md5(data[8:].encode()).hexdigest()
    received_checksum = received_checksum[:8]
    if data[:8] == received_checksum:
        return True
    else:
        return False


def add_checksum(data):
    checksum = hashlib.md5(data.encode()).hexdigest()
    checksum = checksum[:8]
    packet = '{0}{1}'.format(checksum, data).encode()
    return packet





