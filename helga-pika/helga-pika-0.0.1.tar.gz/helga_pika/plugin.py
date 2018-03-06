import smokesignal
from twisted.python.log import err

from helga import log, settings
from helga.plugins import command

import pika
from pika.adapters import twisted_connection
from twisted.internet import defer, reactor, protocol, task

logger = log.getLogger(__name__)


@defer.inlineCallbacks
def run(connection, key=None):
    prefix = settings.NICK
    queue_name = "%s.%s" % (prefix, key)
    channel = yield connection.channel()
    exchange_name = settings.RABBITMQ_EXCHANGE

    try:
        exchange = yield channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
    except Exception:
        logger.exception('unable to declare exchange')

    queue = yield channel.queue_declare(queue=queue_name, auto_delete=True, exclusive=True)

    yield channel.queue_bind(exchange=settings.RABBITMQ_EXCHANGE, queue=queue_name, routing_key=key)

    yield channel.basic_qos(prefetch_count=1)

    queue_object, consumer_tag = yield channel.basic_consume(queue=queue_name, no_ack=False)

    looping_call = task.LoopingCall(read, queue_object, key)

    looping_call.start(0.01)


@defer.inlineCallbacks
def read(queue_object, key):

    ch, method, properties, body = yield queue_object.get()

    if body:
        logger.info('got a new incoming message from the bus, for key: %s' % key)
        smokesignal.emit(key, body)

    yield ch.basic_ack(delivery_tag=method.delivery_tag)


@smokesignal.on('signon')
def init_connection(client):
    """
    Setup the connection to the RabbitMQ server. Currently only 1 instance with
    a single set of credentials is supported.
    """
    required_settings = [
        'RABBITMQ_USER', 'RABBITMQ_PASSWORD',
        'RABBITMQ_HOST', 'RABBITMQ_EXCHANGE'
    ]

    for setting in required_settings:
        if getattr(settings, setting, None) is None:
            raise RuntimeError(
                'Unable to setup connection to RABBITMQ, missing %s setting' % setting
            )

    RABBITMQ_PORT = getattr(settings, 'RABBITMQ_PORT', 5672)

    # Set the connection parameters to connect to HOST on port POST on the
    # / (default) virtual host using the USER and PASSWORD
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(settings.RABBITMQ_HOST,
                                           RABBITMQ_PORT,
                                           '/',
                                           credentials)
    cc = protocol.ClientCreator(reactor, twisted_connection.TwistedProtocolConnection, parameters)
    # unsure why we need both of these again?
    d = cc.connectTCP(settings.RABBITMQ_HOST, RABBITMQ_PORT)
    d.addErrback(fatalError)
    d.addCallback(lambda protocol: protocol.ready)
    for key in settings.RABBITMQ_ROUTING_KEYS:
        try:
            d.addCallback(run, key=key)
            logger.info('Added channel for key: %s' % key)
        except Exception as error:
            logger.exception('got error process adding of a callback')
            logger(error)


@command('bus', help='An interface for the RABBITMQ Message Bus')
def bus(client, channel, nick, message, cmd, args):
    # XXX TODO: add the ability to reconnect or check the status of the connection?
    return


def fatalError(reason):
    #XXX this is extremely poor error handling
    msg = "Unhandled error ocurred"
    logger.critical("%s %s" % (str(reason), msg))
    err(reason, msg)
