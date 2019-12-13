import threading
from time import time


class InputStream(threading.Thread):
    def __init__(self, client):
        super(InputStream, self).__init__()
        self.client = client

    def run(self):
        while not self.client.endCommunication:
            data, information = self.getData()

            self.client.processNewAck(data)

    def getData(self):
        packet, senderInformation = self.client.socket.recvfrom(1024)
        data = self.client.tcp.parseTcpPacket(bytes(packet))
        currentTime = time()
        self.client.setEndOfRtt(data[self.client.tcp.AckNumberIndex] - self.client.segmentSize, currentTime)
        return data, senderInformation
