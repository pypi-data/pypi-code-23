"""Client class.

This client class sends activities to the server.
"""

import threading, queue
import socket
import sys
import logging
from sniffer import SnifferThread

class Client(object):
    """The client class sends messages to the server.
    """

    def __init__(self, server_address):
        self.logger = logging.getLogger('app.client')
        self.logger.info("Starting client...")

        # My ip address
        self.local_address = self.get_my_ip()

        # Create output queue for sniffer thread
        self.result_q = queue.Queue()

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        self.logger.info('connecting to {} port {}'.format(*server_address))
        try:
            self.sock.connect(server_address)
        except:
            self.logger.error("Connection error")
            sys.exit()

        message = "Hello server. I am node {}".format(self.local_address)
        self.send_message(message)

    def start_sniffer(self):
        """Starts the sniffer thread which notifies
        the server about ping packets.
        """

        st = SnifferThread(self.result_q)
        st.start()

        while True:
            message = None
            try:
                message = self.result_q.get()
                self.send_message(message)
            except queue.Empty:
                continue

    def send_message(self, msg):
        """Sends the specified message.
        
        Arguments:
            msg {string} -- A message text.
        """

        try:
            self.logger.debug('Sending {!r}'.format(msg))
            self.sock.sendall(msg)
        except socket.error:
            self.logger.error("Socket error while sending message.")

    def close(self):
        self.logger.debug("Closing socket...")
        self.sock.close()

    def get_my_ip(self):
        """Returns the local IP address of this machine.
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip