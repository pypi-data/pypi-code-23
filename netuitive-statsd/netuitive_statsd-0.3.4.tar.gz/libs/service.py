import logging
import signal

from .daemon import Daemon

logger = logging.getLogger(__name__)


class Service(Daemon):

    """
    Daemon management
    """

    def __init__(self, config, server, poster):
        self.config = config
        self.pid_file = self.config['pid_file']
        Daemon.__init__(self, self.pid_file)
        self.server = server
        self.poster = poster

    def _handle_sigterm(self, signum, frame):
        logger.debug('Sigterm. Stopping.')
        self.server.stop()
        self.poster.stop()

    def run(self):
        # setup signal hooks
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigterm)

        # start the poster thread so we can post data
        self.poster.start()

        try:
            try:
                # start the server so we can accept payloads
                self.server.start()

            except Exception as e:
                # if it doesn't exit normally, log it
                logger.exception('Error starting server')
                raise(e)
        finally:
            # if the server exits normally, stop
            self.poster.stop()
            self.poster.join()
            logger.info("Stopped")
