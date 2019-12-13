import threading
from Tcp import Tcp


class ServerSocket(threading.Thread):
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
        self.buffer = []
        self.droppedPacket = []

    def sendUdpPacket(self, ip, desPort, seqNumber, ackNumber, ack, syn, fin,
                      window=0, urgentPointer=0, headerLength=20, urg=0, psh=0, rst=0):
        self.server.sendUdpPacket(ip, desPort, seqNumber, ackNumber, ack, syn, fin, window, urgentPointer,
                                  headerLength, urg, psh, rst)

    def findNewAck(self, seqNumber):
        newAck = seqNumber + 1
        while (len(self.buffer) != 0) and self.buffer[0] == newAck:
            newAck += 1
            del self.buffer[0]
        return  newAck

    def run(self):
        packet, information = self.currentPacket
        if self.state == "start":
            if packet[self.tcp.DesPortIndex] == self.port and packet[self.tcp.SynIndex] == 1:
                self.state = "handshakeStartSyn"
                self.sendUdpPacket(information[0], information[1], 0, 1, 1, 1, 0)
        elif self.state == "handshakeStartSyn":
            if packet[self.tcp.DesPortIndex] == self.port and packet[self.tcp.AckIndex]:
                self.state = "transferData"
                print ("Connection established.")
        elif self.state == "transferData" and packet[self.tcp.FinIndex] == 1:
            self.state = "terminateCommunication"
            self.sendUdpPacket(information[0], information[1], 0, packet[self.tcp.SeqNumberIndex] +
                               self.segmentSize, 1, 0, 0)
        elif self.state == "transferData":
            if packet[self.tcp.SeqNumberIndex] in self.droppedPacket:
                self.droppedPacket.remove(packet[self.tcp.SeqNumberIndex])
            else:
                print ("Packet " + str(packet[self.tcp.SeqNumberIndex]) + " received.")
                if packet[self.tcp.SeqNumberIndex] == self.currentAck:
                    ack = self.findNewAck(packet[self.tcp.SeqNumberIndex])
                    self.currentAck = ack
                    self.sendUdpPacket(information[0], information[1], 0, ack, 0, 0, 0)
                elif packet[self.tcp.SeqNumberIndex] > self.currentAck:
                    self.buffer.append(packet[self.tcp.SeqNumberIndex])
                    self.buffer.sort()
                else:
                    self.sendUdpPacket(information[0], information[1], 0, self.currentAck, 0, 0, 0)
