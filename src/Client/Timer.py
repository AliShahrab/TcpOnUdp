import threading
from time import sleep


class Timer(threading.Thread):
    def __init__(self, client, timeout, seqNumber):
        super(Timer, self).__init__()
        self.timeout = timeout
        self.client = client
        self.seq = seqNumber
        self.stopCurrentTimer = False

    def run(self):
        print ("timer is start: " + str(self.seq))
        sleep(self.timeout)
        if self.stopCurrentTimer:
            print ("stop timer: " + str(self.seq))
            return
        else:
            print ("timeout raised" + str(self.seq))
            self.client.timeoutReact()
            return

    def stopTimer(self):
        self.stopCurrentTimer = True
        return
