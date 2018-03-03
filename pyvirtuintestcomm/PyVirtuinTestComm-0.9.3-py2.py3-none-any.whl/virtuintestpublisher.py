"""VirtuinTestPublisher is used to publish status updates over AMQP
(via RabbitMQ).
"""
import json
from datetime import datetime
import pika


# pylint: disable=too-many-instance-attributes
class VirtuinTestPublisher(object):
    """VirtuinTestPublisher is used to publish status updates over AMQP
    (via RabbitMQ).

    Attributes:
        None
    """
    def __init__(self, stationName, testName, testUUID=None):
        self.version = '0.9.3'
        self.exName = '{:s}'.format(stationName)
        self.testName = testName
        if testUUID:
            self.testUUID = testUUID
        else:
            dateStr = datetime.now().strftime('%c')
            self.testUUID = str.format('{:s}_{:s}', testName, dateStr)
        self.state = "STARTED"
        self.progress = 0
        self.passed = None
        self.conn = None
        self.ch = None
        self.isOpen = False

    def open(self, hostName='localhost'):
        """Open connection to RabbitMQ
        Args:
            hostName (str): Address of broker
        Returns:
            None
        """
        connParams = pika.ConnectionParameters(host=hostName)
        self.conn = pika.BlockingConnection(connParams)
        self.ch = self.conn.channel()
        self.ch.exchange_declare(exchange=self.exName, exchange_type='fanout')
        self.isOpen = True

    def close(self, tearDown=False):
        """Close connection to RabbitMQ
        Args:
            tearDown (bool, optional):
                To tear down RMQ exchange.
                Useful to clean environment.
        Returns:
            None
        """
        if not self.isOpen:
            return
        if tearDown:
            self.ch.exchange_delete(
                exchange=self.exName
            )
        if self.conn:
            self.conn.close()
        self.conn = None
        self.ch = None
        self.isOpen = False

    def _getBasePayload(self, message="", error=None):
        """Create base payload object to be published
        Args:
            message (str): General status message
            error (str): Error message
        Returns:
            dict: Payload object
        """
        return dict(
            version=self.version,
            status=dict(
                testUUID=self.testUUID,
                testName=self.testName,
                state=self.state,
                passed=self.passed,
                progress=self.progress,
                error=error,
                message=message
            ),
        )

    def _publishData(self, data):
        """Publishes payload object
        Args:
            data (dict): Payload object
        Returns:
            None
        """
        dataStr = json.dumps(data)
        self.ch.basic_publish(exchange=self.exName, routing_key='', body=dataStr)

    def clearStatus(self):
        """Resets status to default values.
        Args:
            None
        Returns:
            None
        """
        self.state = None
        self.progress = 0
        self.passed = None

    def updateStatus(self, state=None, progress=None, passed=None):
        """Update status values.
        Args:
            state (str): State of test (STARTING, ..., FINISHED)
            progress (float): Progress of test [0-100]
            passed (bool): If test passed/failed
        Returns:
            None
        """
        self.state = state if state else self.state
        self.progress = progress if progress is not None else self.progress
        self.passed = passed if passed is not None else self.passed

    def publish(self, message="", error=None, results=None, customDict=None):
        """Publish test status payload.
        Args:
            message (str): General status message
            error (str): Critical error message
            results (dict): Serializable database results object
            customDict (dict): Serializable object to merge into status payload
        Returns:
            None
        """
        data = self._getBasePayload(message, error)
        if results:
            data['results'] = results
        if customDict:
            data.update(customDict)
        self._publishData(data)
