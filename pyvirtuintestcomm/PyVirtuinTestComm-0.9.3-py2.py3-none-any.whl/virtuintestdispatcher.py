"""VirtuinTestDispatcher is used to perform test requests
(start/stop/status) over AMQP (via RabbitMQ).
"""

class VirtuinTestDispatcher(object):
    """VirtuinTestDispatcher is used to perform test requests
    (start/stop/status) over AMQP (via RabbitMQ).

    NOT IMPLEMENTED!!!!

    Attributes:
        None
    """
    def __init__(self):
        raise Exception('VirtuinTestDispatcher not yet implemented.')

    # pylint: disable=unused-argument
    def open(self, brokerAddress='localhost'):
        """Open connection to RabbitMQ
        Args:
            hostName (str): Address of broker
        Returns:
            None
        """
        pass

    def close(self):
        """Close connection to RabbitMQ
        Args:
            None
        Returns:
            None
        """
        pass
