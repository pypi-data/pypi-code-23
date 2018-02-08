import contextlib
import pprint
import re
import traceback
from urllib.parse import urlparse, unquote_plus
from uuid import uuid4

from librabbitmq import Connection

from vireo.helper  import fill_in_the_blank, log, debug_mode_enabled
from vireo.exception import NoConnectionError, InvalidURLError

SHARED_SIGNAL_CONNECTION_LOSS = 1
SHARED_DIRECT_EXCHANGE_NAME   = 'vireo_default_direct_r0'
SHARED_TOPIC_EXCHANGE_NAME    = 'vireo_default_topic_r0'


def make_connection(url, reference_id = None):
    url_component = urlparse(url)

    if not url_component.scheme in ('amqp', 'amqps'):
        raise UnrecognizedProtocolError(url_component.scheme)

    virtual_host = '/'

    if url_component.path and len(url_component.path) > 1:
        virtual_host = unquote_plus(url_component.path[1:])

    params = dict(
        host         = url_component.hostname,
        port         = url_component.port,
        userid       = url_component.username,
        password     = url_component.password,
        virtual_host = virtual_host,
        ssl          = url_component.scheme == 'amqps',
        timeout      = 120,
    )

    if debug_mode_enabled:
        log('debug', 'CONNECTION {}: Will connect with {}'.format(reference_id or 'X', pprint.pformat(params)))

    connection = Connection(**params)
    connection.reference_id = reference_id

    return connection


@contextlib.contextmanager
def active_channel(url, on_connect = None, on_disconnect = None, on_error = None, reference_id = None):
    with active_connection(url, on_connect, on_disconnect, on_error) as connection:
        log('debug', '[active_channel] CONNECTION {}: Opening a channel'.format(reference_id or 'X'))

        with connection.channel() as channel:
            yield channel

        log('debug', '[active_channel] CONNECTION {}: Closed'.format(reference_id or 'X'))


@contextlib.contextmanager
def active_connection(url, on_connect = None, on_disconnect = None, on_error = None, reference_id = None):
    reference_id = reference_id or str(uuid4())

    log('debug', '[active_connection] CONNECTION {}: Connecting to {}'.format(reference_id, re.sub('://[^:]+:[^@]+@', '://', url)))

    try:
        connection = make_connection(url, reference_id)

        log('debug', '[active_connection] CONNECTION {}: Connected'.format(reference_id))

        if on_connect:
            on_connect()
    except Exception as e:
        summary = str(e)

        if on_error:
            on_error(e, summary = summary)

        __raise_no_connection_error(
            'Failed to communicate while opening a channel ({}: {})'.format(type(e).__name__, e),
            on_disconnect,
        )

    log('debug', '[active_connection] CONNECTION {}: Yielding the connection'.format(reference_id))

    yield connection

    log('debug', '[active_connection] CONNECTION {}: Regained the connection'.format(reference_id))

    try:
        connection.close()
    except Exception as e:
        log('warning', '[active_connection] CONNECTION {}: Unexpectedly disconnected while closing the connection. ({})'.format(reference_id, e))

        # bypassed if the connection is no longer available.

    log('debug', '[active_connection] CONNECTION {}: Cleanly disconnected'.format(reference_id))

def __raise_no_connection_error(summary, on_disconnect):
    if on_disconnect:
        on_disconnect(summary = summary)

    raise NoConnectionError(summary)
