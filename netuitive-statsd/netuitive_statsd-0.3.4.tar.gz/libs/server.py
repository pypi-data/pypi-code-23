import logging
import time
import select
import socket

logger = logging.getLogger(__name__)


class Server(object):

    """
    StatsD server
    """

    def __init__(self, config, poster):
        self.config = config
        self.poster = poster
        self.listen_ip = self.config['listen_ip']
        self.listen_port = int(self.config['listen_port'])
        self.prefix = self.config['prefix']
        self.address = (self.listen_ip, self.listen_port)
        self.hostname = config['hostname']
        self.buffer_size = 8192
        self.is_running = False
        self.forward = self.config['forward']

        # if enabled, setup StatsD forwarding
        if self.forward is True:
            self.forward_ip = self.config['forward_ip']
            self.forward_port = int(self.config['forward_port'])

            logger.info("All packets received will be forwarded "
                        "to {0}:{1}".format(
                            self.forward_ip, self.forward_port))
            try:
                self.forward_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
                # self.forward_sock.connect(
                #     (self.forward_ip, self.forward_port))
            except Exception as e:
                logger.exception(
                    "Error while setting up forwarding to an external"
                    " statsd server: {0}".format(str(e)))

    def start(self):
        """
        start our loop
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        try:
            self.socket.bind(self.address)
        except socket.gaierror as e:
            logger.error(e, exc_info=True)
            if self.address[0] == 'localhost':
                self.address = ('127.0.0.1', self.address[1])
                self.socket.bind(self.address)

        except Exception as e:
            logger.exception(
                "Error while listening on " + str(self.address) +
                " statsd server: {0}".format(str(e)))
            self.stop
            raise(e)

        logger.info('Listening on {0}:{1}'.format(
            self.address[0], self.address[1]))

        self.is_running = True

        while self.is_running:
            try:
                ready = select.select([self.socket], [], [], 5)

                if ready[0]:
                    packet = self.socket.recv(self.buffer_size)
                    logger.debug('Received packer: ' + packet.rstrip('\n'))

                    # submit the packet for internal processing
                    timestamp = time.time()
                    self.poster.submit(packet, timestamp)

                    if self.forward is True:
                        logger.debug('Forwarded packet: ' + packet)
                        self.forward_sock.sendto(
                            packet, (self.forward_ip, self.forward_port))

            except select.error as e:
                errno = e[0]
                if errno != 4:
                    # if it's anything other than a interrupted system call,
                    # raise
                    raise

            except (KeyboardInterrupt, SystemExit):
                # if it'a ctrl-c, stop
                self.poster.stop()
                break

            except Exception as e:
                # if it's anything else, throw a fit
                logger.error(e, exc_info=True)
                raise(e)

    def stop(self):
        # stop when asked
        logger.debug("Shutting down")
        self.is_running = False
