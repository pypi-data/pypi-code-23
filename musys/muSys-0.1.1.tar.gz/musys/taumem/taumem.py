import time
import threading
from musys import memchan

'''
    Time keeper class to handle sessions
'''
class chronos(threading.Thread):
    def __init__(self, begin, delta, chan):
        threading.Thread.__init__(self)
        self.begin = begin
        self.delta = delta
        self.signal = True
        self.chan = chan
        self.block = False
        self.clearing = False
        self.quit = False

    '''
        Reset timer
    '''
    def reset_timer(self):
        self.begin = time.time()

    '''
        Thread's primary loop
    '''
    def run(self):
        while self.signal:
            ctime = time.time()
            if ctime - self.begin > self.delta or self.quit:
                self.signal = False
                if not self.block:
                    self.clearing = True
                    self.chan.memory_clear()
                    self.clearing = False
            time.sleep(1)
            
'''
    Memory Session class. The primary passthrough class that manages session settings
'''
class memsess:
    def __init__(self, auth_token, port, local_id, session_length, reset_timeout=False, host=None):
        try:
            self.port = int(port)
            self.session_length = int(session_length)
            self.auth_token = str(auth_token)
            self.local_id = str(local_id)
        except ValueError as _err:
            logging.error(_err)
            raise
        if self.port < 1 or self.port > 65535:
            logging.error("Port number out of range")
            raise Exception("Invalid port")

        self.port = str(self.port)
        if host is not None:
            self.host = host
        else:
            self.host = "localhost"

        self.reset_timeout = reset_timeout
        
        self.chan = memchan(
            self.auth_token,
            self.port,
            self.local_id,
            host=self.host
            )

    '''
        Start a session
    '''
    def beginSession(self):
        self.begin = time.time()
        self.timer = chronos(
            self.begin, 
            self.session_length,
            self.chan
            )
        self.timer.daemon = True
        self.timer.start()

    '''
        Stop a session
    '''
    def closeSession(self):
        self.timer.quit = True
        self.timer.join()
        del self.timer
        self.begin = None

    '''
        Put data on remote machine
    '''
    def put(self, label, data):
        if self.begin is None:
            return None
        if self.reset_timeout:
            self.timer.reset_timer()
        if self.timer.clearing:
            return None
        self.timer.block = True
        return_data = self.chan.put(label, data)
        self.timer.block = False
        return return_data

    '''
        Fetch data from a remote machine
    '''
    def fetch(self, label):
        if self.begin is None:
            return None
        if self.reset_timeout:
            self.timer.reset_timer()
        if self.timer.clearing:
            return None
        self.timer.block = True
        return_data =  self.chan.fetch(label)
        self.timer.block = False
        return return_data