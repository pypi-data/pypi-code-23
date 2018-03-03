"""VirtuinTestHandler is used to handle test start/stop/status
requests over AMQP (via RabbitMQ).
"""

import json
import pika

# pylint: disable=too-many-instance-attributes,duplicate-code
class VirtuinTestHandler(object):
    """VirtuinTestHandler is used to handle test start/stop/status
    requests over AMQP (via RabbitMQ).

    Attributes:
        None
    """
    def __init__(self, stationName):
        self.stationName = stationName
        self.testServerQName = '{:s}'.format(stationName)
        self.conn = None
        self.ch = None
        self.isOpen = False
        self.isListening = False
        self.listener = None

    def open(self, brokerAddress='localhost'):
        """Open connection to RabbitMQ
        Args:
            hostName (str): Address of broker
        Returns:
            None
        """
        host = str.format('{:s}', brokerAddress)
        connParams = pika.ConnectionParameters(host=host)
        self.conn = pika.BlockingConnection(connParams)
        self.ch = self.conn.channel()
        self.ch.queue_declare(queue=self.testServerQName, durable=True)
        self.ch.basic_qos(prefetch_count=1)
        self.isOpen = True

    def close(self):
        """Close connection to RabbitMQ
        Args:
            None
        Returns:
            None
        """
        if not self.isOpen:
            return
        if self.conn:
            self.conn.close()
        self.conn = None
        self.ch = None
        self.isOpen = False
        self.isListening = False
        self.listener = None

    # pylint: disable=unused-argument
    def _consume(self, ch, method, props, body):
        """Called when receieves new request.
        Subsequently calls listener callback.
        Args:
            ch (str): RabbitMQ channel
            method: RabbitMQ method
            props: RabbitMQ props
            body: RabbitMQ Payload
        Returns:
            None
        """
        try:
            jsonData = json.loads(body.decode('utf8'))
            cmd = str(jsonData.get('command', ''))
            rstDict = dict()
            replyQ = props.reply_to
            if self.listener and callable(self.listener):
                rstDict = self.listener(None, jsonData)
            payload = dict(id=props.correlation_id,
                           command=cmd,
                           error=None,
                           success=True)
            if isinstance(rstDict, dict):
                payload.update(rstDict)
            payloadBuffer = json.dumps(payload)
            corrID = props.correlation_id
            queueOptions = pika.BasicProperties(correlation_id=corrID)
            self.ch.basic_publish(exchange='',
                                  routing_key=replyQ,
                                  properties=queueOptions,
                                  body=payloadBuffer)
            self.ch.basic_ack(delivery_tag=method.delivery_tag)
        # pylint: disable=broad-except
        except Exception as err:
            if self.listener and callable(self.listener):
                self.listener(err, None)

    def listen(self, listener):
        """Start listening for requests. This method blocks.
        Args:
            listener (callable): callback function called when
            request is received (error: str, result: dict) => dict
        Returns:
            str: consumerTag
        """
        if not self.isOpen or self.isListening:
            raise Exception('Connection not open or already listening.')
        try:
            self.listener = listener
            self.isListening = True
            consumerTag = self.ch.basic_consume(
                self._consume,
                queue=self.testServerQName
            )
            self.ch.start_consuming()  # This blocks
            return consumerTag
        # pylint: disable=broad-except,unused-variable
        except Exception as err:
            return None
