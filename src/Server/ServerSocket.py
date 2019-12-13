import threading
import time

from Tcp import Tcp


class ServerSocket (threading.Thread):
    def __init__(self, port, udpSocket, srcIp, srcPort, firstPacket, server):
        super(ServerSocket, self).__init__()
        self.server = server
        self.socket = udpSocket
        self.srcIp = srcIp
        self.srcPort = srcPort
        self.port = port
        self.tcp = Tcp()
        self.currentPacket = firstPacket
        self.state = "start"
        self.segmentSize = 1
        self.count = 1
        self.currentAck = 0
        self.cwnd = 20
        self.windows = [0] * self.cwnd

    def sendUdpPacket(self, ip, desPort, seqNumber, ackNumber, ack, syn, fin,
                      window=0, urgentPointer=0, headerLength=20, urg=0, psh=0, rst=0):
        self.server.sendUdpPacket(ip, desPort, seqNumber, ackNumber, ack, syn, fin, window, urgentPointer,
                                  headerLength, urg, psh, rst)

    def run(self):
        packet, information = self.currentPacket
        if self.state == "start":
            if packet[self.tcp.DesPortIndex] == self.port and packet[self.tcp.SynIndex] == 1:
                print ("handshakeStartSyn")
                self.state = "handshakeStartSyn"
                self.sendUdpPacket(information[0], information[1], 0, 1, 1, 1, 0)
        elif self.state == "handshakeStartSyn":
            if packet[self.tcp.DesPortIndex] == self.port and packet[self.tcp.AckIndex]:
                self.state = "transferData"
                print ("Connection established.")
        elif self.state == "transferData":
            print ("seq number received: " + str(packet[self.tcp.SeqNumberIndex]) + ", current ack: " +
                   str(self.currentAck))
            print "%.20f" % time.time()
            print ("seq number received = " + str(packet[self.tcp.SeqNumberIndex]))
            ack = packet[self.tcp.SeqNumberIndex] + self.segmentSize
            if packet[self.tcp.SeqNumberIndex] == 4 and self.count == 1:
                print ("herrrrr")
                self.count = 0
            else:
                if packet[self.tcp.SeqNumberIndex] == self.currentAck:
                    self.currentAck = ack
                    print ("hey")
                    self.sendUdpPacket(information[0], information[1], 0, ack, 0, 0, 0)
                # else:
                    # self.windows[]

        print ("end")
