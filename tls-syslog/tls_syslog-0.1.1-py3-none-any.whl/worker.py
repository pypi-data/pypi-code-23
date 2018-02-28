import socket
import ssl
import threading
import queue


class TCPLoggingThread(threading.Thread):
    """
    A daemon-thread used to send messages to syslog over a TCP/TLS socket in the background, so that
    the TCP socket doesn't block the application's main thread.
    """

    # Block for 500ms when waiting for a message in the queue. ``self.should_terminate`` will therefore
    # be checked at least this often, even in the queue is completely empty.
    queue_block_timeout = 0.5


    def __init__(self, address, timeout, queue, should_terminate, ssl_kwargs):
        super().__init__(daemon=True)
        self.address = address
        self.timeout = timeout
        self.queue = queue
        self.should_terminate = should_terminate
        self.ssl_kwargs = ssl_kwargs
        self._open_socket()


    def run(self):
        """
        Run the daemon-thread.

        Consumers messages from the queue and sends them over the TLS socket until both the
        queue is empty and the should_terminate event is set.
        """
        while True:
            # If should_terminate, close the socket and exist
            if self.queue.empty() and self.should_terminate.is_set():
                self._close_socket()
                return

            # Block waiting for a log message to write
            try:
                message = self.queue.get(block=True, timeout=self.queue_block_timeout)
            except queue.Empty:
                continue

            # Write the message to the socket
            try:
                self._send_message(message)
            except Exception as e:
                print(e)

            # Register with the queue that the item has completed
            self.queue.task_done()


    def _open_socket(self):
        if getattr(self, 'socket', None):
            self._close_socket()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        self.socket = ssl.wrap_socket(sock, **self.ssl_kwargs)
        self.socket.connect(self.address)


    def _close_socket(self):
        self.socket.close()


    def _send_message(self, message):
        try:
            self.socket.send(message)
        except OSError:
            self._open_socket()
            self.socket.send(message)
