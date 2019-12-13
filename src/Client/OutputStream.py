import threading
from time import sleep

from Tcp import Tcp


class OutputStream(threading.Thread):
    def __init__(self, packets, socket):
        super(OutputStream, self).__init__()
        self.packets = packets
        self.tcp = Tcp()
        self.socket = socket

    def run(self):
        while len(self.packets) != 0:
            sleep(0.1)
            data = self.tcp.parseTcpPacket(self.packets[0][2])
            print ("send packet: " + str(data[self.tcp.SeqNumberIndex]))
            self.sendUdpPacketManual(self.packets[0][0], self.packets[0][1], self.packets[0][2])
            del self.packets[0]
        print ("close output stream!")

    def sendUdpPacketManual(self, ip, desPort, packet):
        self.socket.sendto(str(packet), (ip, desPort))
