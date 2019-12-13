import struct


class Tcp:
    def __init__(self):
        self.SrcPortIndex = 0
        self.DesPortIndex = 1
        self.SeqNumberIndex = 2
        self.AckNumberIndex = 3
        self.HeaderLengthIndex = 4
        self.UrgIndex = 5
        self.AckIndex = 6
        self.PshIndex = 7
        self.RstIndex = 8
        self.SynIndex = 9
        self.FinIndex = 10
        self.WindowsIndex = 11
        self.CheckSumIndex = 12
        self.UrgentPointerIndex = 13

    @staticmethod
    def parseTcpPacket(packet):
        result = [struct.unpack("<H", packet[0:2])[0]]

        help = struct.unpack(">H", packet[12:14])[0]
        fin = help % 2
        syn = (help >> 1) % 2
        rst = (help >> 2) % 2
        psh = (help >> 3) % 2
        ack = (help >> 4) % 2
        urg = (help >> 5) % 2
        headerLength = (help >> 12) % 16

        result.append(struct.unpack("<H", packet[2:4])[0])
        result.append(struct.unpack("<I", packet[4:8])[0])
        result.append(struct.unpack("<I", packet[8:12])[0])
        result.append(headerLength)
        result.append(urg)
        result.append(ack)
        result.append(psh)
        result.append(rst)
        result.append(syn)
        result.append(fin)
        result.append(struct.unpack("<H", packet[14:16])[0])
        result.append(struct.unpack("<H", packet[16:18])[0])
        result.append(struct.unpack("<H", packet[18:20])[0])

        return result

    def validPacket(self, packet):
        srcPort = packet[self.SrcPortIndex]
        desPort = packet[self.DesPortIndex]
        seqNumber = packet[self.SeqNumberIndex]
        ackNumber = packet[self.AckNumberIndex]
        fin = packet[self.FinIndex]
        syn = packet[self.SynIndex]
        rst = packet[self.RstIndex]
        psh = packet[self.AckIndex]
        ack = packet[self.AckIndex]
        urg = packet[self.UrgIndex]
        headerLength = packet[self.HeaderLengthIndex]
        window = packet[self.WindowsIndex]
        urgentPointer = packet[self.UrgentPointerIndex]

        checkSum = self.calculateChecksum(srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst,
                                          syn, fin, window, urgentPointer)

        return checkSum == packet[self.CheckSumIndex]

    @staticmethod
    def calculateChecksum(srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst, syn, fin,
                          window, urgentPointer):
        checkSum = srcPort + desPort
        checkSum += seqNumber + (seqNumber >> 16)
        checkSum += ackNumber + (ackNumber >> 16)
        checkSum += fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5) + (
                    (headerLength << 12) & 0xf000)
        checkSum += window
        checkSum += urgentPointer
        checkSum = checkSum % 0x10000
        return checkSum

    @staticmethod
    def createTcpSegment(srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst, syn, fin,
                         window, urgentPointer):
        # region calculate checksum
        checkSum = Tcp.calculateChecksum(srcPort, desPort, seqNumber, ackNumber, headerLength, urg, ack, psh, rst,
                                         syn, fin, window, urgentPointer)
        # end region

        # region create header
        header = b''
        header += struct.pack("<H", srcPort)
        header += struct.pack("<H", desPort)
        header += struct.pack("<I", seqNumber)
        header += struct.pack("<I", ackNumber)
        help1 = (headerLength << 12) & 0xf000
        help1 += fin
        help1 += syn << 1
        help1 += rst << 2
        help1 += psh << 3
        help1 += ack << 4
        help1 += urg << 5
        header += struct.pack(">H", help1)
        header += struct.pack("<H", window)
        header += struct.pack("<H", checkSum)
        header += struct.pack("<H", urgentPointer)
        # end region
        return header


tcp = Tcp()
m = tcp.createTcpSegment(0x1234, 0x5678, 0x12345678, 0x42316782, 7, 1, 0, 0, 1, 1, 0, 0x2341, 0x123)
# f = file("test.hex", "w")
# f.write(m)

a = [0, 1, 2, 3, 4, 5]
print (a[0:1])
v = 0x1234
vc = struct.pack("<H", v)
