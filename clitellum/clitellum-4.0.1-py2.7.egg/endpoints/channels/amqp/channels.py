import re
import socket
import threading

import pika

from clitellum.core import compressors, loggerManager
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.basechannels import OutBoundChannel, Channel, InBoundChannel
from clitellum.endpoints.channels.exceptions import ConnectionError
from clitellum.endpoints.channels.amqp.configuration import AmqpHostConfiguration

__author__ = 'sergio'


class BaseAmqpChannel(object):
    '''
    Clase base de un canal amqp
    '''

    def __init__(self, amqp_config: AmqpHostConfiguration):
        self._amqp_config = amqp_config
        self._connection = None
        self._channel = None

    def _connect_point(self):
        try:
            if not self._connection is None and self._connection.is_open:
                self._connection.close()

            parameters = pika.connection.Parameters()
            parameters.host = self._amqp_config.get_server()
            parameters.heartbeat = 60
            parameters.port = self._amqp_config.get_port()
            parameters.credentials = pika.PlainCredentials(username=self._amqp_config.get_user(), \
                                                        password=self._amqp_config.get_password())

            self._connection = pika.BlockingConnection(parameters=parameters)
            self._channel = self._connection.channel()

            if self._amqp_config.get_exchange().must_be_created():
                self._channel.exchange_declare(exchange=self._amqp_config.get_exchange().get_name(), \
                durable=True, exchange_type=self._amqp_config.get_exchange().get_type(), \
                auto_delete=False)

        except Exception as ex:
            raise ConnectionError(ex)

    def _close_point(self):
        if self._connection.is_open():
            self._connection.close()


class OutBoundAmqpChannel(OutBoundChannel, BaseAmqpChannel):
    '''
    Clase que implementa un canal de salida con el protocolo amqp
    '''

    def __init__(self, amqp_config: AmqpHostConfiguration, \
                reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(), 
                maxReconnections=Channel.MAX_RECONNECTIONS, compressor=compressors.DefaultCompressor()):


        BaseAmqpChannel.__init__(self, amqp_config)
        OutBoundChannel.__init__(self, self._amqp_config.get_exchange().get_name(), \
                                 reconnectionTimer, maxReconnections, \
                                 compressor, useAck=amqp_config.get_use_ack())

    def _connect_point(self):
        BaseAmqpChannel._connect_point(self)
        if self._useAck:
            self._channel.confirm_delivery()

    def _close_point(self):
        BaseAmqpChannel._close_point(self)

    def _send(self, message, routing_key='', content_encoding='utf-8', content_type='text/plain'):
        try:
            properties = pika.BasicProperties(content_type=content_type, delivery_mode=2, content_encoding=content_encoding)
            if routing_key == '':
                return self._channel.basic_publish(body=message,
                                                   exchange=self._amqp_config.get_exchange().get_name(),
                                                   routing_key='',
                                                   properties=properties)
            else:
                return self._channel.basic_publish(body=message,
                                                   exchange=self._amqp_config.get_exchange().get_name(),
                                                   routing_key=routing_key,
                                                   properties=properties)

        except socket.error as ex:
            loggerManager.get_endPoints_logger().error("Error: %s" % ex)
            raise ConnectionError("Se ha perdido la conexcion con el servidor AMPQ")
        except Exception as ex:
            loggerManager.get_endPoints_logger().error("Error: %s" % ex)
            raise ConnectionError('Error al enviar el elemento %s' % ex)

class InBoundAmqpChannel(InBoundChannel, BaseAmqpChannel):

    def __init__(self, amqp_config: AmqpHostConfiguration, \
                 reconnectionTimer=reconnectiontimers.CreateLogarithmicTimer(),
                 maxReconnections=Channel.MAX_RECONNECTIONS, receptionTimeout=10,
                 compressor=compressors.DefaultCompressor(),
                 max_threads=1):

        BaseAmqpChannel.__init__(self, amqp_config)
        InBoundChannel.__init__(self, self._amqp_config.get_exchange().get_name(), \
                                reconnectionTimer, maxReconnections, compressor=compressor,
                                useAck=self._amqp_config.get_use_ack())

        self._reception_timeout = receptionTimeout
        self.__is_consuming = False
        self.__max_threads = max_threads
        self.__semaforo = threading.Semaphore(max_threads)
        self.__ack_semaforo = threading.Semaphore()
        self.__consumer_tag = None


    def _connect_point(self):
        BaseAmqpChannel._connect_point(self)

        try:
            if self._amqp_config.get_queue().must_be_created():
                self._channel.queue_declare(queue=self._amqp_config.get_queue().get_name(), \
                                            durable=True, auto_delete=False)
                for key in self._amqp_config.get_queue().get_routing_keys():
                    self._channel.queue_bind(queue=self._amqp_config.get_queue().get_name(), \
                                             exchange=self._amqp_config.get_exchange().get_name(), \
                                             routing_key=key)

            self._channel.basic_qos(prefetch_size=self._amqp_config.get_qos().get_prefetch_size(),
                                    prefetch_count=self._amqp_config.get_qos().get_prefetch_count())

        except Exception as ex:
            raise ConnectionError(ex)

    def _close_point(self):
        BaseAmqpChannel._close_point(self)

    def __read_message(self, channel, method_frame, header_frame, body):
        if self.__max_threads > 1:
            self.__semaforo.acquire()
            msg = {"body": body, "channel" : channel, "delivery_tag": method_frame.delivery_tag}
            threading.Thread(target=self.__worker, kwargs={"msg": msg}).start()
        else:
            msg_info = {"channel": channel, "delivery_tag": method_frame.delivery_tag}
            self._processMessage(body, 0, msg_info)

    def __worker(self, msg):
        msg_info = {"channel": msg['channel'], "delivery_tag": msg['delivery_tag']}
        self._processMessage(msg['body'], 0, msg_info)
        self.__semaforo.release()

    def _startReceive(self):
        self.__consumer_tag = self._channel.basic_consume(self.__read_message,
                                                          queue=self._amqp_config.get_queue().get_name(),
                                                          no_ack=False)
        self._connection.add_timeout(self._reception_timeout, self._stopReceive)
        self._channel.start_consuming()

    def _wait_method(self):
        pass

    def _stopReceive(self):
        self._channel.basic_cancel(self.__consumer_tag)

    def _sendAck(self, object, idMessage):
        self.__ack_semaforo.acquire()
        object["channel"].basic_ack(delivery_tag=object["delivery_tag"])
        self.__ack_semaforo.release()
