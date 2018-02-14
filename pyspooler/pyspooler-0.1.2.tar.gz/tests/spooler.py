import signal

from spooler.spooler import Spooler
from spooler.task import Task
from spooler.connectors.file_system import FSConnector


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


conn = FSConnector("/tmp/pyspooler")
spooler = Spooler(conn)


def stop():
    spooler.stop()


def test_spooler():
    task = Task(stop)
    conn.add_task(task)
    with timeout(1):
        spooler.consume()
