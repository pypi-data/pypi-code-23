# -*- coding: utf-8 -*-

import threading
import json

import logging
logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_LAYOUT = "%(asctime)-15s - P%(process)-5d T%(thread)-5d [%(levelname)-8s] - %(message)s"


def add_log_handler(log_handler, log_level=DEFAULT_LOG_LEVEL, log_layout=DEFAULT_LOG_LAYOUT, log_filter=None):
    log_handler.setLevel(log_level)
    log_handler.setFormatter(logging.Formatter(log_layout))
    if log_filter:
        log_handler.addFilter(log_filter)
    logging.getLogger().addHandler(log_handler)


def remove_log_handler(log_handler):
    logging.getLogger().removeHandler(log_handler)
    log_handler.close()


class ThreadNameFilter(logging.Filter):
    def __init__(self, name=None):
        super(ThreadNameFilter, self).__init__()
        self.name = name or threading.current_thread().name

    def filter(self, record):
        return record.threadName == self.name


class RedisHandler(logging.Handler):
    def __init__(self, url, key, db=None, includes=None, excludes=None, **kwargs):
        import redis
        super(RedisHandler, self).__init__()
        self.__key = key
        self.__includes = includes
        self.__excludes = excludes or ("args", "exc_info", "msg", "stack_info")
        self.__redis = redis.from_url(url, db, **kwargs)
        self.__redis.delete(self.__key)     # remove key if exists

    def emit(self, record):
        data = {}
        for k, v in record.__dict__.items():
            if (self.__includes and k in self.__includes) or (self.__excludes and k not in self.__excludes):
                data[k] = v
        s = json.dumps(data)
        self.__redis.rpush(self.__key, s)

        # Redis maintain connection pool, don't need to close the connection manually.
        # def close(self):
        #     pass


class AmqpHandler(logging.Handler):
    def __init__(self, url, exchange_name, exchange_type, routing_key, includes=None, excludes=None):
        import kombu
        super(AmqpHandler, self).__init__()
        self.__includes = includes
        self.__excludes = excludes or ("args", "exc_info", "msg", "stack_info")
        self.__conn = kombu.Connection(url)
        # self.__conn.connect()
        exchange = kombu.Exchange(exchange_name, exchange_type, durable=False)
        self.__producer = self.__conn.Producer(exchange=exchange, routing_key=routing_key)

    def emit(self, record):
        """
        The amqp module also print the log when call publish, this will cause maximum recursion depth exceeded.
        """
        if not record.name == "amqp":
            data = {}
            for k, v in record.__dict__.items():
                if (self.__includes and k in self.__includes) or (self.__excludes and k not in self.__excludes):
                    data[k] = v
            self.__producer.publish(data, retry=True, delivery_mode=2)

    def close(self):
        self.acquire()
        try:
            logger.debug("Release %s for AmqpHandler", self.__conn)
            self.__conn.release()
        finally:
            self.release()
            super(AmqpHandler, self).close()


# class LogAmqpConsumer(ConsumerMixin, threading.Thread):
#     def __init__(self, url, exchange_name, exchange_type, routing_key):
#         super(LogAmqpConsumer, self).__init__()
#         queue_name = routing_key + "@" + socket.gethostbyname(socket.gethostname())
#         self.connection = kombu.Connection(url)
#         exchange = kombu.Exchange(exchange_name, exchange_type, durable=False)
#         self.queue = kombu.Queue(queue_name, exchange, routing_key, exclusive=True)
#
#     def get_consumers(self, Consumer, channel):
#         return [Consumer([self.queue], callbacks=[self.on_message], accept=['json'])]
#
#     def on_message(self, body, message):
#         logger.debug("RECEIVED MESSAGE: %r" % (body, ))
#         message.ack()
#
#     def run(self):
#         ConsumerMixin.run(self)
#
#     def stop(self):
#         self.should_stop = True
#         self.join()
