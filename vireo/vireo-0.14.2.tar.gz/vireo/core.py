from uuid import uuid4

from .exception import NoConnectionError
from .helper    import log


class Core(object):
    def __init__(self, driver):
        self._identifier = str(uuid4())
        self._driver     = driver

        self._log('debug', 'Driver Class: {}.{}'.format(self._driver.__module__, type(self._driver).__name__))

    @property
    def id(self) -> str:
        """ Observer Identifier """
        return self._identifier

    def emit(self, event_name, data = None, options = None, error_suppressed = True):
        """ Emit a message to a particular (shared) event.

            .. code-block:: python

                app.emit('security.alert.intrusion', {'ip': '127.0.0.1'})

        """
        reference_id = str(uuid4())

        self._log('debug', 'TRANSACTION {}: Sending "{}" with {}'.format(reference_id, event_name, data))

        try:
            self._driver.publish(event_name, data, options or {})

            self._log('debug', 'TRANSACTION {}: Sent'.format(reference_id))
        except NoConnectionError as e:
            self._log('error', 'TRANSACTION {}: ERROR {}.{}: {}'.format(reference_id, e.__module__, type(e).__name__, e))

            if error_suppressed:
                self._log('warn', 'TRANSACTION {}: Error surpressed'.format(reference_id, e))

                return

            raise NoConnectionError('Failed to emit an event {}.'.format(event_name))

        self._log('debug', 'TRANSACTION {}: Complete'.format(reference_id, event_name, data))

    def broadcast(self, event_name, data = None, options = None, error_suppressed = True):
        """ Broadcast a message to a particular (distributed) event.

            .. code-block:: python

                app.broadcast('system.down', {'service_category': 'go_board'})

        """
        reference_id = str(uuid4())

        self._log('debug', 'TRANSACTION {}: Broadcasting "{}" with {}'.format(reference_id, event_name, data))

        try:
            self._driver.broadcast(event_name, data, options or {})

            self._log('debug', 'TRANSACTION {}: Broadcasted'.format(reference_id))
        except NoConnectionError as e:
            self._log('error', 'TRANSACTION {}: ERROR {}.{}: {}'.format(reference_id, e.__module__, type(e).__name__, e))

            if error_suppressed:
                self._log('warn', 'TRANSACTION {}: Error surpressed'.format(reference_id, e))

                return

            raise NoConnectionError('Failed to broadcast an event {}.'.format(event_name))

        self._log('debug', 'TRANSACTION {}: Complete'.format(reference_id, event_name, data))

    def _log(self, level, message):
        log(level, '{} {}: {}'.format(self.__class__.__name__, self.id, message))
