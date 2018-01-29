import json, os, datetime, urllib, time, pika, inspect


class ServiceQ:

    class PayloadProperties(object):
        pass

    class ServiceRunner(object):
        def __init__(self, callback, service_instance):
            self.__callback = callback
            self.__service_instance = service_instance

        def __call__(self, ch, method, properties, body):
            payload = json.loads(body)

            self.__service_instance\
                .set_last_request_method(method)\
                .set_last_request_properties(properties)\
                .set_last_payload(payload)

            self.__callback(payload['body'], self.__service_instance)

    def __init__(self, service):
        self.__service = service
        self.__payloadStatus = 200

        self.__last_request_method = None
        self.__last_payload = None
        self.__last_request_properties = None

        self.__connection = pika.BlockingConnection(ServiceQ.__ampqParams)
        self.__channel = self.__connection.channel()

    def set_last_payload(self, payload):
        self.__last_payload = payload
        return self

    def set_last_request_method(self, method):

        self.__last_request_method = method
        return self

    def set_last_request_properties(self, properties):

        self.__last_request_properties = properties
        return self

    def acknowledge(self):

        if self.__last_request_method is None:
            # list of errors https://docs.python.org/3/library/exceptions.html#exception-hierarchy
            raise ResourceWarning("This request has been already acknowledged")

        self.__channel.basic_ack(delivery_tag=self.__last_request_method.delivery_tag)

        self.__last_request_method = None
        return self

    def reply(self, message):

        if self.__last_request_method is not None:
            self.__channel.basic_publish(exchange='',
                         routing_key=self.__last_request_properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=self.__last_request_properties.correlation_id),
                         body=self.__prepare_payload(message, 'REPLY'))
        else:
            raise ResourceWarning("This request has been already acknowledged")

        return self

    def serve(self, callback):

        #todo listen on topic -- no_ack = True

        self.__channel.queue_declare(queue=self.__service, durable=True, auto_delete=False)
        self.__channel.basic_consume(ServiceQ.ServiceRunner(callback, self), queue=self.__service, no_ack=False)
        self.__channel.start_consuming()

        return self

    def publish(self, **kwargs):

        topic = ''
        if hasattr(kwargs, 'topic'):
            topic = kwargs['topic']

        payload = kwargs['payload']
        payload = self.__prepare_payload(payload, "PUBLISH")

        properties = self.__prepare_payload_properties(method="PUBLISH")

        self.__channel.queue_declare(queue=self.__service, durable=True, auto_delete=False)
        self.__channel.basic_publish(exchange='', routing_key=self.__service, body=payload)

        return self

    def __prepare_payload(self, msg, method):

        payload = {
            "status": self.__payloadStatus,
            "statusMsg": self.__get_status_message(self.__payloadStatus),
            "meta": {
                "creator": os.path.realpath(inspect.stack()[2][1]),
                "queue": {
                    "name": self.__service
                },
                "method": method,
                "date": {
                    "atom": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                    "mtimestamp": time.time(),
                    "timestamp": int(time.time())
                }
            },
            "body": msg
        }

        if self.__last_payload is not None:
            payload['meta']['servingTimeSec'] = time.time() - self.__last_payload['meta']['date']['mtimestamp']

        return json.dumps(payload)

    def __prepare_payload_properties(self, **kwargs):

        properties = ServiceQ.PayloadProperties()

        if hasattr(kwargs, 'correlation_id'):
            properties.correlation_id = kwargs['correlation_id']

        return properties

    def __get_status_message(self, code):

        if code == 100: text = 'Continue'
        elif code == 101: text = 'Switching Protocols'
        elif code == 200: text = 'OK'
        elif code == 201: text = 'Created'
        elif code == 202: text = 'Accepted'
        elif code == 203: text = 'Non-Authoritative Information'
        elif code == 204: text = 'No Content'
        elif code == 205: text = 'Reset Content'
        elif code == 206: text = 'Partial Content'
        elif code == 300: text = 'Multiple Choices'
        elif code == 301: text = 'Moved Permanently'
        elif code == 302: text = 'Moved Temporarily'
        elif code == 303: text = 'See Other'
        elif code == 304: text = 'Not Modified'
        elif code == 305: text = 'Use Proxy'
        elif code == 400: text = 'Bad Request'
        elif code == 401: text = 'Unauthorized'
        elif code == 402: text = 'Payment Required'
        elif code == 403: text = 'Forbidden'
        elif code == 404: text = 'Not Found'
        elif code == 405: text = 'Method Not Allowed'
        elif code == 406: text = 'Not Acceptable'
        elif code == 407: text = 'Proxy Authentication Required'
        elif code == 408: text = 'Request Time-out'
        elif code == 409: text = 'Conflict'
        elif code == 410: text = 'Gone'
        elif code == 411: text = 'Length Required'
        elif code == 412: text = 'Precondition Failed'
        elif code == 413: text = 'Request Entity Too Large'
        elif code == 414: text = 'Request-URI Too Large'
        elif code == 415: text = 'Unsupported Media Type'
        elif code == 500: text = 'Internal Server Error'
        elif code == 501: text = 'Not Implemented'
        elif code == 502: text = 'Bad Gateway'
        elif code == 503: text = 'Service Unavailable'
        elif code == 504: text = 'Gateway Time-out'
        elif code == 505: text = 'HTTP Version not supported'
        else: text = 'Unknown http status code'

        return text

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    @classmethod
    def settings(cls, settings):
        cls.__settings = settings

        settings = ServiceQ.__settings
        url = os.environ.get('CLOUDAMQP_URL',
                             'amqp://' + settings['username'] + ':' + settings['password'] + '@' +
                             settings['host'].replace('amqp://','') + '/' +
                             urllib.quote_plus(settings['vhost']))

        cls.__ampqParams = pika.URLParameters(url)
        cls.__ampqParams.socket_timeout = 5

    @staticmethod
    def __settings(settings):
        return 'static method called'

