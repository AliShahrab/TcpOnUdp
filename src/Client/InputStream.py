import threading


class InputStream(threading.Thread):
    def __init__(self, client):
        super(InputStream, self).__init__()
        self.client = client

    def run(self):
        print ("input stream is running now")
        while not self.client.endCommunication:
            data, information = self.getData()
            # sleep(0.5)
            # print (data)
            # sleep(0.5)

            self.client.processNewAck(data)
        print ("close input stream")

    def getData(self):
        packet, senderInformation = self.client.socket.recvfrom(1024)
        data = self.client.tcp.parseTcpPacket(bytes(packet))
        return data, senderInformation
