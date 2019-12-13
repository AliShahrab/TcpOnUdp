import logging
import socket
import random
import datetime
from time import sleep, time
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
        self.aliveTime = 10
        self.rtt = []
        self.estimatedRtt = 1
        self.alpha = 0.125
        self.devRtt = 0
        self.beta = 0.25
        self.cwndLog = []

    def sendData(self, data):
        try:
            self.currentData = data
            self.segments = [0] * (len(data) // self.segmentSize + 1)
            inputStream = InputStream(self)
            inputStream.start()
            self.startTimer(self.sendBase)
            self.sendDataToServerWithBaseAndCwndManual(self.sendBase, self.cwnd)

        except:
            logging.error("exception")

    def timeoutReact(self):
        self.cwnd = self.cwnd // 2
        self.cwndLog.append([time(), self.cwnd])
        print ("Packet " + str(self.sendBase) + " Dropped.")
        self.startTimer(self.sendBase)
        self.sendDataToServerWithBaseAndCwndManual(self.sendBase, 1)
        return

    def startTimer(self, seqNumber):
        self.timer = Timer(self, self.timeout, seqNumber, self.timeoutReact)
        self.timer.start()

    def stopTimer(self):
        self.timer.stopTimer()

    def processNewAck(self, data):
        sleep(0.1)
        self.updateTimeout(data[self.tcp.AckNumberIndex])
        ack = data[self.tcp.AckNumberIndex]
        if ack > len(self.currentData):
            self.stopTimer()
            self.endCommunication = True
            return
        if ack > self.sendBase:
            self.stopTimer()
            oldBase = self.sendBase
            oldCwnd = self.cwnd
            self.sendBase = ack / self.segmentSize
            if self.cwnd < 20:
                self.cwnd += 1
            self.cwndLog.append([time(), self.cwnd])

            self.startTimer(self.sendBase)
            self.sendDataToServerWithBaseAndCwndManual(oldBase + oldCwnd, (self.sendBase - oldBase) + 1)

        return

    def findIndexOfPacketInRtt(self, seqNumber):
        for i in range(len(self.rtt)):
            if self.rtt[i][0] == seqNumber:
                return i
        return -1

    def setStartOfRtt(self, seqNumber, timeLocal):
        indexOfRtt = self.findIndexOfPacketInRtt(seqNumber)
        if indexOfRtt == -1:
            self.rtt.append([seqNumber, timeLocal, -1, -1])
        else:
            self.rtt[indexOfRtt][1] = timeLocal

    def setEndOfRtt(self, seqNumber, timeLocal):
        indexOfRtt = self.findIndexOfPacketInRtt(seqNumber)
        diff = timeLocal - self.rtt[indexOfRtt][1]
        self.rtt[indexOfRtt][2] = diff
        self.rtt[indexOfRtt][3] = timeLocal
        return diff

    def getSampleRtt(self, seqNumber):
        indexOfRtt = self.findIndexOfPacketInRtt(seqNumber)
        return self.rtt[indexOfRtt][2]

    def updateEstimatedAndDevRtt(self, newAck):
        seqNumber = newAck - self.segmentSize
        sampleRtt = self.getSampleRtt(seqNumber)
        self.estimatedRtt = self.estimatedRtt * (1 - self.alpha) + sampleRtt * self.alpha
        self.updateDevRtt(self.estimatedRtt, sampleRtt)

    def updateDevRtt(self, estimatedRtt, sampleRtt):
        self.devRtt = self.devRtt * (1 - self.beta) + abs(estimatedRtt - sampleRtt) * self.beta

    def updateTimeout(self, newAck):
        self.updateEstimatedAndDevRtt(newAck)
        self.timeout = self.estimatedRtt + 4 * self.devRtt

    def sendUdpPacketManual(self, ip, desPort, packet):
        self.socket.sendto(str(packet), (ip, desPort))

    def sendDataToServerWithBaseAndCwndManual(self, base, length):
        currentPackets = []
        for i in range(length):
            if base + i < len(self.segments):
                packet = self.createTcpPacketManual(self.port, (base + i) * self.segmentSize, 0, 0, 0, 0)
                currentPackets.append([self.ip, self.port, packet])
        if len(currentPackets) != 0:
            newOutputStream = OutputStream(currentPackets, self)
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

    def sendDataToServerWithBaseAndCwnd(self, base, length):
        for i in range(length):
            if base + i < len(self.segments):
                self.sendDataToServer((base + i) * self.segmentSize)

    def sendDataToServer(self, seqNumber, ackNumber=0):
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
        self.sendUdpPacket(self.ip, self.port, 0, 0, 0, 1, 0)
        while True:
            packet, information = self.getData()
            if packet[self.tcp.DesPortIndex] == self.srcPort and packet[self.tcp.SynIndex] == 1 and \
                    packet[self.tcp.AckIndex] == 1:
                self.sendUdpPacket(self.ip, self.port, 0, 0, 1, 0, 0)
                break
        print ("client " + str(self.srcPort) + " connected.")

    def terminateCommunication(self):
        self.sendUdpPacket(self.ip, self.port, 0, 0, 0, 0, 1)
        while True:
            packet, information = self.getData()
            if packet[self.tcp.DesPortIndex] == self.srcPort and packet[self.tcp.AckIndex] == 1:
                self.sendUdpPacket(self.ip, self.port, 0, 0, 1, 0, 0)
                break
        print ("connection closed")

        f = open("cwndLog.txt", "w")
        result = ""
        base = self.cwndLog[0][0]
        for log in self.cwndLog:
            result += str(log[0] - base) + ":" + str(log[1]) + "\n"
        f.write(result)
        f.close()

        f = open("sampleRttLog.txt", "w")
        result = ""
        for log in self.rtt:
            result += str(log[0]) + ":" + str(log[2]) + "\n"
        f.write(result)
        f.close()

    def createTimeoutForEndCommunication(self):
        timer = Timer(self, self.aliveTime, None, self.terminateCommunication)
        timer.start()

    def connect(self):
        self.establishConnection()
        self.createTimeoutForEndCommunication()


ips = "127.0.0.1"
ports = 8080

c = Client('127.0.0.1', 8080)
c.connect()
sleep(0.1)
b = [0] * 30
c.sendData(b)
