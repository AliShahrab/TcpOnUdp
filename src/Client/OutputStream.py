import threading
from time import sleep, time

from Tcp import Tcp


class OutputStream(threading.Thread):
    def __init__(self, packets, client):
        super(OutputStream, self).__init__()
        self.packets = packets
        self.tcp = Tcp()
        self.client = client

    def run(self):
        while len(self.packets) != 0:
            sleep(0.1)
            data = self.tcp.parseTcpPacket(self.packets[0][2])
            self.sendUdpPacketManual(self.packets[0][0], self.packets[0][1], self.packets[0][2])
            del self.packets[0]
            # print "send packet:" + str(data[self.tcp.SeqNumberIndex])

    def sendUdpPacketManual(self, ip, desPort, packet):
        data = self.tcp.parseTcpPacket(self.packets[0][2])
        self.client.setStartOfRtt(data[self.tcp.SeqNumberIndex], time())
        self.client.socket.sendto(str(packet), (ip, desPort))
