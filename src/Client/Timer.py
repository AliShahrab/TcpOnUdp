import threading
from time import sleep


class Timer(threading.Thread):
    def __init__(self, client, timeout, seqNumber, callBackAfterTimeout):
        super(Timer, self).__init__()
        self.timeout = timeout
        self.client = client
        self.seq = seqNumber
        self.stopCurrentTimer = False
        self.callBackAfterTimeout = callBackAfterTimeout

    def run(self):
        sleep(self.timeout)
        if self.stopCurrentTimer:
            return
        else:
            self.callBackAfterTimeout()
            return

    def stopTimer(self):
        self.stopCurrentTimer = True
        return
