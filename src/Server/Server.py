import socket
from ServerSocket import *
from Tcp import Tcp


class Server:
    def __init__(self, port):
        self.ServerSocketIndex = 2
        self.ip = '127.0.0.1'
        self.port = port
        self.serverSockets = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.tcp = Tcp()
        self.srcIpIndex = 0
        self.srcPortIndex = 1

    def getData(self):
        packet, senderInformation = self.socket.recvfrom(1024)
        data = self.tcp.parseTcpPacket(bytes(packet))
        return data, senderInformation

    def existSocket(self, ip, port):
        for information in self.serverSockets:
            if information[self.srcIpIndex] == ip and information[self.srcPortIndex] == port:
                return True
        return False

    def addSocketInformation(self, ip, port, serverSocket):
        self.serverSockets.append([ip, port, serverSocket])

    def sendUdpPacket(self, ip, desPort, seqNumber, ackNumber, ack, syn, fin,
                      window, urgentPointer, headerLength, urg, psh, rst):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        srcPort = self.port
        packet = self.tcp.createTcpSegment(srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst,
                                           syn, fin, window, urgentPointer)
        client.sendto(str(packet), (ip, desPort))

    def getServerSocket(self, ip, port):
        for information in self.serverSockets:
            if information[self.srcIpIndex] == ip and information[self.srcPortIndex] == port:
                return information[self.ServerSocketIndex]
        return None

    def removeServerSocket(self, ip, port):
        for information in self.serverSockets:
            if information[self.srcIpIndex] == ip and information[self.srcPortIndex] == port:
                self.serverSockets.remove(information)
                return 0
        return -1

    def run(self):
        while True:
            data, senderInformation = self.getData()
            if not self.tcp.validPacket(data):
                continue
            if not self.existSocket(senderInformation[0], senderInformation[1]):
                newSocket = ServerSocket(self.port, self.socket, senderInformation[0], senderInformation[1],
                                         (data, senderInformation), self)
                newSocket.start()
                self.addSocketInformation(senderInformation[0], senderInformation[1], newSocket)
            else:
                currentServerSocket = self.getServerSocket(senderInformation[0], senderInformation[1])
                currentServerSocket.currentPacket = (data, senderInformation)
                currentServerSocket.run()
                if currentServerSocket.state == "terminateCommunication":
                    result = self.removeServerSocket(senderInformation[0], senderInformation[1])
                    if result == 0:
                        print ("Connection " + str(senderInformation[1]) + " closed")


server = Server(8080)
server.run()
