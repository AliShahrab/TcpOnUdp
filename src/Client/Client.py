import logging
import socket
import random
import datetime
from time import sleep
from InputStream import InputStream
from OutputStream import OutputStream
from Timer import Timer
from Tcp import Tcp


class Client:
    def __init__(self, initialIp, initialPort):
        self.ip = initialIp
        self.port = initialPort
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.srcPort = -1
        self.tcp = Tcp()
        self.segmentSize = 1
        self.segments = []
        self.sendBase = 0
        self.cwnd = 1
        self.timeout = 1
        self.timer = None
        self.currentData = None
        self.packetForSend = []
        self.endCommunication = False
        self.endSendData = True

    def sendData(self, data):
        try:
            print ("send data is initial")
            self.currentData = data
            self.segments = [0] * (len(data) // self.segmentSize + 1)
            inputStream = InputStream(self)
            inputStream.start()
            # sleep(10)
            print ("setup input stream")
            self.startTimer(self.sendBase)
            self.sendDataToServerWithBaseAndCwndManual(self.sendBase, self.cwnd)
            print ("setup streams")

        except:
            print ("hey")

        # thread.exit()

    def timeoutReact(self):
        print ("timeout react")
        self.cwnd = self.cwnd // 2
        self.sendDataToServerWithBaseAndCwndManual(self.sendBase, 1)
        # self.startTimer()
        return

    def startTimer(self, seqNumber):

        self.timer = Timer(self, self.timeout, seqNumber)
        print ("timer want to start")
        self.timer.start()

    def stopTimer(self):
        self.timer.stopTimer()

    def processNewAck(self, data):
        ack = data[self.tcp.AckNumberIndex]
        print ("this ack is received: " + str(ack))
        if ack > len(self.currentData):
            self.stopTimer()
            print ("send of data is complete")
            self.endCommunication = True
            return
        if ack > self.sendBase:
            self.stopTimer()

            oldBase = self.sendBase
            oldCwnd = self.cwnd
            self.sendBase = ack / self.segmentSize
            self.cwnd += 1

            self.startTimer(self.sendBase)
            self.sendDataToServerWithBaseAndCwndManual(oldBase + oldCwnd, (self.sendBase - oldBase) + 1)

            # self.updateTimeout()

        return

    def sendUdpPacketManual(self, ip, desPort, packet):
        self.socket.sendto(str(packet), (ip, desPort))

    def sendDataToServerWithBaseAndCwndManual(self, base, length):
        # print ("send packet from " + str(base) + " to " + str(base + length))
        currentPackets = []
        for i in range(length):
            if base + i < len(self.segments):
                packet = self.createTcpPacketManual(self.port, (base + i) * self.segmentSize, 0, 0, 0, 0)
                currentPackets.append([self.ip, self.port, packet])

        if len(currentPackets) != 0:
            newOutputStream = OutputStream(currentPackets, self.socket)
            newOutputStream.start()

    def createTcpPacketManual(self, desPort, seqNumber, ackNumber, ack, syn, fin,
                              window=0, urgentPointer=0, headerLength=20, urg=0, psh=0, rst=0):
        packet = Tcp.createTcpSegment(self.srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst,
                                      syn,
                                      fin, window, urgentPointer)
        return packet

    def getData(self):
        packet, senderInformation = self.socket.recvfrom(1024)
        data = self.tcp.parseTcpPacket(bytes(packet))
        return data, senderInformation

    def updateTimeout(self):
        return

    def sendDataToServerWithBaseAndCwnd(self, base, length):
        # print ("send packet from " + str(base) + " to " + str(base + length))
        for i in range(length):
            if base + i < len(self.segments):
                self.sendDataToServer((base + i) * self.segmentSize)

    def sendDataToServer(self, seqNumber, ackNumber=0):
        print ("send packet " + str(seqNumber) + " to server")
        self.sendUdpPacket(self.ip, self.port, seqNumber, ackNumber, 0, 0, 0)

    def sendUdpPacket(self, ip, desPort, seqNumber, ackNumber, ack, syn, fin,
                      window=0, urgentPointer=0, headerLength=20, urg=0, psh=0, rst=0):
        packet = Tcp.createTcpSegment(self.srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst,
                                      syn,
                                      fin, window, urgentPointer)
        self.socket.sendto(str(packet), (ip, desPort))

    @staticmethod
    def bindSocket(currentSocket):
        randomNumber = 0
        random.seed(datetime.datetime.now())
        while True:
            try:
                randomNumber = random.randint(9000, 10000)
                currentSocket.bind(('', randomNumber))
                break
            except Exception:
                logging.error("port " + str(randomNumber) + "is busy now")
        return randomNumber

    def establishConnection(self):
        self.srcPort = self.bindSocket(self.socket)
        print (self.srcPort)
        self.sendUdpPacket(self.ip, self.port, 0, 0, 0, 1, 0)
        while True:
            packet, information = self.getData()
            if packet[self.tcp.DesPortIndex] == self.srcPort and packet[self.tcp.SynIndex] == 1 and \
                    packet[self.tcp.AckIndex] == 1:
                self.sendUdpPacket(self.ip, self.port, 0, 0, 1, 0, 0)
                break
        print ("client " + str(self.srcPort) + " connected.")

    def connect(self):
        self.establishConnection()


ips = "127.0.0.1"
ports = 8080

c = Client('127.0.0.1', 8080)
c.connect()
sleep(0.1)
b = [0, 1, 2, 3, 4]
c.sendData(b)
