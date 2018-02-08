import contextlib
import re
import traceback
from uuid import uuid4

from pika            import BlockingConnection
from pika.connection import URLParameters
from pika.exceptions import ConnectionClosed, ChannelClosed, IncompatibleProtocolError

from ...helper  import fill_in_the_blank, log
from .exception import NoConnectionError

SHARED_SIGNAL_CONNECTION_LOSS = 1
SHARED_DIRECT_EXCHANGE_NAME   = 'vireo_default_direct_r0'
SHARED_TOPIC_EXCHANGE_NAME    = 'vireo_default_topic_r0'


def make_connection(url):
    init_params = URLParameters(url)

    return BlockingConnection(init_params)


@contextlib.contextmanager
def active_connection(url, on_connect = None, on_disconnect = None, on_error = None, reference_id = None):
    reference_id = reference_id or str(uuid4())

    log('debug', '[active_connection] CONNECTION {}: Connecting to {}'.format(reference_id, re.sub('://[^:]+:[^@]+@', '://', url)))

    try:
        connection = make_connection(url)
        channel    = connection.channel()

        log('debug', '[active_connection] CONNECTION {}: Connected'.format(reference_id))

        if on_connect:
            on_connect()
    except IncompatibleProtocolError as e:
        summary = str(e)

        if on_error:
            on_error(e, summary = summary)

        raise NoConnectionError(summary)
    except ChannelClosed as e:
        __raise_no_connection_error(
            'Failed to communicate while opening a channel ({}: {})'.format(type(e).__name__, e),
            on_disconnect,
        )
    except ConnectionClosed as e:
        __raise_no_connection_error(
            'Failed to connect while opening a connection ({}: {})'.format(type(e).__name__, e),
            on_disconnect,
        )

    log('debug', '[active_connection] CONNECTION {}: Yielding the connection'.format(reference_id))

    yield channel

    log('debug', '[active_connection] CONNECTION {}: Regained the connection'.format(reference_id))

    try:
        channel.close()
        connection.close()
    except ChannelClosed as e:
        log('warning', '[active_connection] CONNECTION {}: Unexpectedly disconnected while closing the channel. ({})'.format(reference_id, e))

        # bypassed if the connection is no longer available.
    except ConnectionClosed as e:
        log('warning', '[active_connection] CONNECTION {}: Unexpectedly disconnected while closing the connection. ({})'.format(reference_id, e))

        # bypassed if the connection is no longer available.

    log('debug', '[active_connection] CONNECTION {}: Cleanly disconnected'.format(reference_id))

def __raise_no_connection_error(summary, on_disconnect):
    if on_disconnect:
        on_disconnect(summary = summary)

    raise NoConnectionError(summary)
