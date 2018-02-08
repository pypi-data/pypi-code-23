import json
import threading
import time
import uuid

from pika            import BasicProperties
from pika.exceptions import ConnectionClosed

from ...helper import fill_in_the_blank, log

from .consumer  import Consumer
from .exception import NoConnectionError, SubscriptionNotAllowedError
from .helper    import active_connection, SHARED_DIRECT_EXCHANGE_NAME, SHARED_TOPIC_EXCHANGE_NAME, SHARED_SIGNAL_CONNECTION_LOSS


DEFAULT_ALLOWED_RETRY_COUNT = 5


class Driver(object):
    """ Driver for RabbitMQ

        :param          url:               the URL to the server (``str`` for a single connection or ``list`` for rotation)
        :param list     consumer_classes:  the list of :class:`.consumer.Consumer`-based classes
        :param bool     unlimited_retries: the flag to disable limited retry count.
        :param callable on_connect:        a callback function when the message consumption begins.
        :param callable on_disconnect:     a callback function when the message consumption is interrupted due to unexpected disconnection.
        :param callable on_error:          a callback function when the message consumption is interrupted due to exception raised from the main callback function.

        :param dict default_publishing_options:                  the default options for publishing (normal)
        :param dict default_broadcasting_options:                the default options for publishing (broadcast)
        :param dict default_consuming_shared_queue_options:      the default options for consuming share queue
        :param dict default_consuming_distributed_queue_options: the default options for consuming distributed queue

        ``default_publishing_options`` and ``default_broadcasting_options`` only take ``exchange``
        to allow overriding the default exchange.

        ``default_consuming_shared_queue_options`` and ``default_consuming_distributed_queue_options``
        will have the data structure like this::

            {
                'exchange': {
                    'name': str, # It is "exchange" in pika's exchange_declare.
                    'type': str, # It is "exchange_type" in pika's exchange_declare.
                }
            }

        Here is an example for ``on_connect``.

        .. code-block:: Python

            def on_connect(consumer = None, controller_id = None, route = None, queue_name = None, summary = None):
                ...

        Here is an example for ``on_disconnect``.

        .. code-block:: Python

            def on_disconnect(consumer = None, controller_id = None, route = None, queue_name = None, summary = None):
                ...

        Here is an example for ``on_error``.

        .. code-block:: Python

            def on_error(exception, consumer = None, controller_id = None, route = None, queue_name = None, summary = None):
                ...

        Where:
        * ``exception`` is the (raised) exception object.
        * ``consumer`` is the associate consumer object (optional).
        * ``controller_id`` is the associate ID (optional).
        * ``route`` is the affected route (optional).
        * ``queue_name`` is the affected queue name (optional).
        * ``summary`` is the summary of the event (optional).
    """
    def __init__(self, url, consumer_classes = None, unlimited_retries = False, on_connect = None,
                 on_disconnect = None, on_error = None, default_publishing_options : dict = None,
                 default_broadcasting_options : dict = None, default_consuming_shared_queue_options : dict = None,
                 default_consuming_distributed_queue_options : dict = None, auto_acknowledge = False,
                 send_sigterm_on_disconnect = True):
        for consumer_class in consumer_classes or []:
            assert isinstance(consumer_class, Consumer), 'This ({}) needs to be a subclass of vireo.drivers.rabbitmq.Consumer.'.format(consumer_class)

        self._url              = url
        self._consumer_classes = consumer_classes or []
        self._async_listener   = None
        self._shared_stream    = []
        self._consumers        = []
        self._has_term_signal  = False
        self._active_routes    = []
        self._auto_acknowledge = auto_acknowledge

        self._send_sigterm_on_disconnect = send_sigterm_on_disconnect

        self._default_publishing_options                  = default_publishing_options                  or {}
        self._default_broadcasting_options                = default_broadcasting_options                or {}
        self._default_consuming_shared_queue_options      = default_consuming_shared_queue_options      or {}
        self._default_consuming_distributed_queue_options = default_consuming_distributed_queue_options or {}

        self._unlimited_retries = unlimited_retries
        self._on_connect        = on_connect
        self._on_disconnect     = on_disconnect
        self._on_error          = on_error

        self._requested_url_counter = 0 # used for rotation
        self._total_url_count       = 1 if isinstance(self._url, str) else len(self._url)

    @property
    def url(self):
        connection_url = self._url

        if isinstance(self._url, (tuple, list)):
            self._requested_url_counter += 1

            connection_index = self._requested_url_counter % self._total_url_count
            connection_url   = self._url[connection_index]

        return connection_url

    def set_on_connect(self, on_connect):
        self._on_connect = on_connect

    def set_on_disconnect(self, on_disconnect):
        self._on_disconnect = on_disconnect

    def set_on_error(self, on_error):
        self._on_error = on_error

    def setup_async_cleanup(self):
        """ Prepare to cleanly join all consumers asynchronously. """
        if self._async_listener and self._async_listener.is_alive():
            raise SubscriptionNotAllowedError('Unable to consume messages as this driver is currently active.')

        self._async_listener = threading.Thread(target = self.join)
        self._async_listener.start()

    def stop_consuming(self):
        """ Send the signal to stop consumption. """
        self._has_term_signal = True

    def join(self):
        """ Synchronously join all consumers."""
        try:
            while True:
                if self._has_term_signal:
                    log('warning', 'Stopping all route listeners')

                    break

                if SHARED_SIGNAL_CONNECTION_LOSS in self._shared_stream:
                    log('error', 'Unexpected connection loss detected')
                    log('warning', 'Terminating all route listeners')

                    break

                time.sleep(1)
        except KeyboardInterrupt:
            log('warning', 'SIGTERM received')
            log('debug', 'Terminating all route listeners')

        connection_losed = SHARED_SIGNAL_CONNECTION_LOSS in self._shared_stream

        for consumer in self._consumers:
            if not connection_losed:
                if not consumer.is_alive():
                    log('info', 'Route {}: Already stopped listening (not alive).'.format(consumer.route))

                    continue

                log('warning', 'Route {}: Sending the signal to stop listening.'.format(consumer.route))
                consumer.stop()

            try:
                log('debug', 'Route {}: Terminating the listener.'.format(consumer.route))
                consumer._stop()
            except AssertionError: # this is raised if the thread lock is still locked.
                log('warning', 'Route {}: Probably already stopped'.format(consumer.route))

            if not consumer.is_alive():
                log('info', 'Route {}: Termination confirmed (killed)'.format(consumer.route))

                continue

            log('debug', 'Route {}: Waiting the listener to join back to the parent thread.'.format(consumer.route))
            consumer.join()
            log('info', 'Route {}: Termination confirmed (joined).'.format(consumer.route))

        if connection_losed:
            raise NoConnectionError('Unexpectedly losed the connection during message consumption')

    def publish(self, route, message, options = None, allowed_retry_count = DEFAULT_ALLOWED_RETRY_COUNT):
        """ Synchronously publish a message

            :param str route:   the route
            :param str message: the message
            :param dict options: additional options for basic_publish
            :param bool allowed_retry_count: the flag to allow auto-retry on connection failure
        """
        default_parameters = self._generate_default_publish_options(
            self._default_publishing_options,
            SHARED_DIRECT_EXCHANGE_NAME,
            route,
            message,
        )

        options = fill_in_the_blank(options or {}, default_parameters)

        self._do_publish(route, message, options, allowed_retry_count)

    def _do_publish(self, route, message, options, allowed_retry_count):
        with active_connection(self.url, **self._get_callback_map(allowed_retry_count)) as channel:
            try:
                log('debug', '[_do_publish] Publishing: route={} message={} options={}'.format(route, message, options))
                channel.basic_publish(**options)
                log('debug', '[_do_publish] Published: route={} message={} options={}'.format(route, message, options))
            except ConnectionClosed:
                if allowed_retry_count:
                    log('warn', '[_do_publish] RETRY Publishing: route={} message={} options={}'.format(route, message, options))

                    self._do_publish(
                        route,
                        message,
                        options,
                        allowed_retry_count = allowed_retry_count - 1,
                    )

                    return

                log('error', '[_do_publish] Failed to publish: route={} message={} options={}'.format(route, message, options))

                if self._on_disconnect:
                    async_callback = threading.Thread(target = self._on_disconnect, daemon = True)
                    async_callback.start()

                raise NoConnectionError('Unexpectedly losed the connection while publishing a message')

    def broadcast(self, route, message, options = None, allowed_retry_count = DEFAULT_ALLOWED_RETRY_COUNT):
        """ Broadcast a message to a particular route.

            :param str route:    the route
            :param str message:  the message
            :param dict options: additional options for basic_publish
        """
        default_parameters = self._generate_default_publish_options(
            self._default_broadcasting_options,
            SHARED_TOPIC_EXCHANGE_NAME,
            route,
            message,
        )

        options = fill_in_the_blank(options or {}, default_parameters)

        if 'exchange' not in options or not options['exchange']:
            options['exchange'] = SHARED_TOPIC_EXCHANGE_NAME

        exchange_name = options['exchange']

        self._do_broadcast(exchange_name, route, message, options, allowed_retry_count)

    def _do_broadcast(self, exchange_name, route, message, options, allowed_retry_count):
        with active_connection(self.url, **self._get_callback_map(allowed_retry_count)) as channel:
            try:
                log('debug', '[_do_broadcast] Declaring a shared topic exchange')

                channel.exchange_declare(
                    exchange      = exchange_name,
                    exchange_type = 'topic',
                    passive       = False,
                    durable       = True,
                    auto_delete   = False,
                )

                log('debug', '[_do_broadcast] Declared a shared topic exchange')

                log('debug', '[_do_broadcast] Broadcasting: route={} message={} options={}'.format(route, message, options))
                channel.basic_publish(**options)
                log('debug', '[_do_broadcast] Broadcasted: route={} message={} options={}'.format(route, message, options))

            except ConnectionClosed:
                if allowed_retry_count:
                    log('warn', '[_do_broadcast] RETRY Broadcasting: route={} message={} options={}'.format(route, message, options))

                    self._do_broadcast(
                        exchange_name,
                        route,
                        message,
                        options,
                        allowed_retry_count = allowed_retry_count - 1,
                    )

                    return

                log('error', '[_do_broadcast] Failed to broadcast: route={} message={} options={}'.format(route, message, options))

                if self._on_disconnect:
                    async_callback = threading.Thread(target = self._on_disconnect, daemon = True)
                    async_callback.start()

                raise NoConnectionError('Unexpectedly losed the connection while broadcasting an event')

    def observe(self, route, callback, resumable, distributed, options = None,
                simple_handling = True, controller_id = None, delay_per_message = 0):
        consumer_class = Consumer

        for overriding_consumer_class in self._consumer_classes:
            if overriding_consumer_class.can_handle_route(route):
                consumer_class = overriding_consumer_class

                break

        if not controller_id:
            controller_id = str(uuid.uuid4())

            log('info', 'Observer on {} will have the self-assigned controller ID {}'.format(route, controller_id))

        default_options = self._default_consuming_distributed_queue_options if distributed else self._default_consuming_shared_queue_options
        given_options   = options or {}

        queue_options    = fill_in_the_blank(given_options.get('queue',    {}), default_options.get('queue',    {}))
        exchange_options = fill_in_the_blank(given_options.get('exchange', {}), default_options.get('exchange', {}))

        parameters = dict(
            url               = self.url,
            route             = route,
            callback          = callback,
            shared_stream     = self._shared_stream,
            resumable         = resumable,
            distributed       = distributed,
            queue_options     = queue_options,
            simple_handling   = simple_handling,
            unlimited_retries = self._unlimited_retries,
            on_connect        = self._on_connect,
            on_disconnect     = self._on_disconnect,
            on_error          = self._on_error,
            controller_id     = controller_id,
            exchange_options  = exchange_options,
            auto_acknowledge  = self._auto_acknowledge,
            send_sigterm_on_disconnect = self._send_sigterm_on_disconnect,
            delay_per_message = delay_per_message,
        )

        consumer = consumer_class(**parameters)

        self._consumers.append(consumer)

        consumer.start()

        return consumer

    def _get_callback_map(self, allowed_retry_count):
        callback_required = allowed_retry_count <= 0

        return dict(
            on_connect    = self._on_connect    if callback_required else None,
            on_disconnect = self._on_disconnect if callback_required else None,
            on_error      = self._on_error      if callback_required else None,
        )

    def _generate_default_publish_options(self, default_publishing_options, default_exchange_name,
                                          route, message):
        return {
            'exchange'    : default_publishing_options.get('exchange', default_exchange_name),
            'routing_key' : route,
            'body'        : json.dumps(message),
            'properties'  : BasicProperties(content_type = 'application/json'),
        }
