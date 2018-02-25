from io import BytesIO
from multiprocessing import Process, Queue
import sys
import time
import traceback

from contracts import contract
from setproctitle import setproctitle  # @UnresolvedImport @UnusedImport
from termcolor import colored

from .utils import LineSplitter


class ProcessManager(object):

    status_queue = Queue()

    @contract(args='tuple')
    def __init__(self, f, args, name, restart):
        self.f = f
        self.args = args
        self.name = name
        self.restart = restart

    def start(self):
        args = (ProcessManager.status_queue, self.f, self.args, self.name, self.restart)
        self.p = Process(target=manager, args=args)
        self.p.daemon = True
        self.p.start()

    def join(self):
        self.process.join()


def manager(status_queue, f, args, name, restart):
    setproctitle('dt-swarm ' + name)

    nrestarts = 0
    min_restart_interval = 10
    restart_multiplier = 2.0

    def get_prefix():
        if nrestarts == 0:
            return colored(name, attrs=['dark'])
        else:
            return colored(name + '!%d' % nrestarts, 'red')

    t1 = lambda s: '%s|%s' % (get_prefix(), s)
    original_stdout = sys.stdout
    sys.stdout = AddPrefixStream(original_stdout, t1)

    status_queue.put(('starting', name))
    while True:
        last_restart = time.time()
        try:
            f(*args)
        except Exception as e:
            nrestarts += 1
            min_restart_interval *= restart_multiplier
            print(traceback.format_exc(e))
            if not restart:
                break

        now = time.time()
        wait_until = last_restart + min_restart_interval
        if now < wait_until:
            wait = wait_until - now
            print('waiting %d s before starting' % wait)
            time.sleep(wait)

        status_queue.put(('restart', name))

    status_queue.put(('exit', name))
    print('peaceful exit')


class AddPrefixStream(object):

    def __init__(self, to, transform):
        self.buffer = BytesIO()
        self.line_splitter = LineSplitter()
        self.to = to
        self.transform = transform

    def write(self, s):
        self.line_splitter.append_chars(s)
        lines = self.line_splitter.lines()
        for line in lines:
            self.to.write(self.transform(line) + '\n')
        self.to.flush()

    def flush(self):
        pass

