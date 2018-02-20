from multiprocessing.dummy import Value, Lock

class Counter(object):
    def __init__(self):
        self.val = Value('i', 0)
        self.lock = Lock()

    def inc(self):
        with self.lock:
            self.val.value += 1

    def dec(self):
        with self.lock:
            self.val.value -= 1

    def value(self):
        with self.lock:
            return self.val.value