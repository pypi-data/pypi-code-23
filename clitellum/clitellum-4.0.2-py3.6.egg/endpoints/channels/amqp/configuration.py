import re
import socket
import threading

import pika

from clitellum.core import compressors, loggerManager
from clitellum.endpoints.channels import reconnectiontimers

__author__ = 'sergio'

class AmqpHostConfiguration(object):
    '''
    Configuracion del host de amqp
    '''
    def __init__(self):
        self._server = None
        self._port = 5672
        self._exchange = ExchangeConfiguration()
        self._user = 'guest'
        self._password = 'guest'
        self._queue = QueueConfiguration()
        self._use_ack = True
        self._qos = QosConfiguration()

    def get_server(self):
        '''
        Devuelve Nombre del host o direccion ip del servidor amqp
        '''
        return self._server

    def set_server(self, value):
        '''
        Establece el host o direccion ip del servidor amqp
        '''
        self._server = value

    def get_port(self):
        '''
        Numero del puerto de conexion del servidor amqp, por defecto 5672
        '''
        return self._port

    def set_port(self, value):
        '''
        Establece el puerto de conexion con el servidor amqp
        '''
        self._port = value

    def get_exchange(self):
        '''
        Exchange de conexion del servidor amqp
        '''
        return self._exchange

    def get_user(self):
        '''
        Devuelve nombre del usuario para conectar al servidor amqp
        '''
        return self._user

    def set_user(self, value):
        '''
        Establece nombre del usuario para conectar al servidor amqp
        '''
        self._user = value

    def get_password(self):
        '''
        Contraseña del usuario para conectar al servidor amqp
        '''
        return self._password

    def set_password(self, value):
        '''
        Establece la contraseña del usuario para conectar al servidor amqp
        '''
        self._password = value

    def get_queue(self):
        '''
        Devuelve la configuracion de la queue
        '''
        return self._queue

    def set_use_ack(self, value):
        self._use_ack = value

    def get_use_ack(self):
        return self._use_ack

    def get_qos(self):
        return self._qos
    
class ExchangeConfiguration(object):
    '''
    Configuracion del exchange de amqp
    '''
    def __init__(self):
        self._name = None
        self._type = ExchangeType.TOPIC
        self._create = True

    def get_name(self):
        '''
        Nombre del exchange
        '''
        return self._name

    def set_name(self, value):
        '''
        Establece el nombre del exchange
        '''
        self._name = value

    def get_type(self):
        '''
        Tipo de exchange
        '''
        return self._type

    def set_type(self, value):
        '''
        Tipo de exchange
        '''
        self._type = value

    def must_be_created(self):
        '''
        Indica si el exchange debe crearse en el momento de la conexion, por defecto True
        '''
        return self._create

    def set_created(self, value):
        '''
        Indica si el exchange debe crearse en el momento de la conexion, por defecto True
        '''
        self._create = value

class QueueConfiguration(object):
    '''
    Configuracion de la cola de amqp
    '''
    def __init__(self):
        self._name = None
        self._create = True
        self._routing_keys = []

    def get_name(self):
        '''
        Nombre de la cola donde conectarse
        '''
        return self._name

    def set_name(self, value):
        '''
        Establece el nombre de la cola donde conectarse
        '''
        self._name = value

    def get_routing_keys(self):
        '''
        Devuelve la lista de routing keys
        '''
        return self._routing_keys

    def add_routing_key(self, key):
        '''
        Inserta una nueva clave de enrutamiento para la cola
        '''
        self._routing_keys.append(key)

    def add_routing_keys(self, keys):
        '''
        Inserta un grupo de claves de enrutamiento
        '''
        for key in keys:
            self.add_routing_key(key)

    def must_be_created(self):
        '''
        Indica si el exchange debe crearse en el momento de la conexion, por defecto True
        '''
        return self._create

    def set_created(self, value):
        '''
        Indica si el exchange debe crearse en el momento de la conexion, por defecto True
        '''
        self._create = value

class QosConfiguration(object):
    '''
    Configuracion de la calidad del servicio
    '''

    def __init__(self):
        self._prefetch_size = 0
        self._prefetch_count = 10000

    def set_prefetch_size(self, size):
        '''
        Establece el prefetch size del amqp
        '''
        self._prefetch_size = size

    def get_prefetch_size(self):
        '''
        Devuelve el prefetch size del amqp
        '''
        return self._prefetch_size

    def set_prefetch_count(self, count):
        '''
        Establece el prefetch count del amqp
        '''
        self._prefetch_count = count

    def get_prefetch_count(self):
        '''
        Devuelve el prefetch count del amqp
        '''
        return self._prefetch_count

class ExchangeType(object):
    '''
    Enumeracion con los tipos posibles de exchange
    '''
    DIRECT = 'direct'
    TOPIC = 'topic'

class AmqpHostConfigurationBuilder(object):
    '''
    Clase que genera un constructor de la configuracion del host
    '''

    OUT_BOUND_CHANNEL = 'outboundchannel'
    IN_BOUND_CHANNEL = 'inboundchannel'

    @classmethod
    def create(cls):
        return AmqpHostConfigurationBuilder()

    def __init__(self):
        self._uri = None
        self._exchange_type = 'direct'
        self._type = AmqpHostConfigurationBuilder.OUT_BOUND_CHANNEL
        self._create_exchange = True
        self._create_queue = True
        self._user = 'guest'
        self._password = 'guest'
        self._use_ack = True
        self._prefetch_size = 0
        self._prefetch_count = 10000

    def set_uri(self, uri):
        '''
        Establece la uri del servidor de amqp
        '''
        self._uri = uri
        return self

    def set_direct_exchange(self):
        '''
        Establece el tipo direct en el exchange
        '''
        self._exchange_type = ExchangeType.DIRECT
        return self

    def set_topic_exchange(self):
        '''
        Establece el tipo topic en el exchange
        '''
        self._exchange_type = ExchangeType.TOPIC
        return self

    def set_create_exchange(self, value):
        '''
        Establece que se cree el exchange durante la conexion
        '''
        self._create_exchange = value
        return self

    def set_create_queue(self, value):
        '''
        Establece que se cree el cola durante la conexion
        '''
        self._create_queue = value
        return self

    def set_is_out_bound(self):
        '''
        Indica que la uri es para un canal de salida
        '''
        self._type = AmqpHostConfigurationBuilder.OUT_BOUND_CHANNEL
        return self

    def set_is_in_bound(self):
        '''
        Indica que la uri es para un canal de entrada
        '''
        self._type = AmqpHostConfigurationBuilder.IN_BOUND_CHANNEL
        return self

    def set_credentials(self, user, password):
        '''
        Establece la credenciales de conexion
        '''
        self._user = user
        self._password = password
        return self

    def set_use_ack(self, value):
        self._use_ack = value
        return self

    def set_prefetch_count(self, count):
        '''
        Establece el prefetch count del amqp
        '''
        self._prefetch_count = count
        return self
    
    def set_prefetch_size(self, size):
        '''
        Establece el prefetch size del amqp
        '''
        self._prefetch_size = size
        return self

    def build(self):
        '''
        Crea una instancia de la configuracion del servidor
        '''
        ret = AmqpHostConfiguration()
        ret.set_user(self._user)
        ret.set_password(self._password)
        ret.set_use_ack(self._use_ack)

        if self._type == AmqpHostConfigurationBuilder.OUT_BOUND_CHANNEL:
            self._extract_exchange(ret)
        else:
            if self._exchange_type == ExchangeType.DIRECT:
                self._extract_queue_direct(ret)
            else:
                self._extract_queue_topic(ret)

        ret.get_exchange().set_type(self._exchange_type)
        ret.get_exchange().set_created(self._create_exchange)
        ret.get_queue().set_created(self._create_queue)
        ret.get_qos().set_prefetch_count(self._prefetch_count)
        ret.get_qos().set_prefetch_size(self._prefetch_size)
        return ret

    def _extract_exchange(self, host_config: AmqpHostConfiguration):
        match = re.search(r'^amqp://(.*):(\d+)/(.*)', self._uri)
        if match:
            host_config.set_server(match.group(1))
            host_config.set_port(int(match.group(2)))
            host_config.get_exchange().set_name(match.group(3))
        else:
            raise NameError("Invalid host name", self._uri)

    def _extract_queue_topic(self, host_config: AmqpHostConfiguration):

        match = re.search(r'^amqp://(.*):(\d+)/(.*)/(.*)/(.*)', self._uri)
        if match:
            host_config.set_server(match.group(1))
            host_config.set_port(int(match.group(2)))
            host_config.get_exchange().set_name(match.group(3))
            host_config.get_queue().set_name(match.group(4))
            host_config.get_queue().add_routing_keys(match.group(5).split(';'))
        else:
            raise NameError("Invalid host name", self._uri)

    def _extract_queue_direct(self, host_config: AmqpHostConfiguration):

        match = re.search(r'^amqp://(.*):(\d+)/(.*)/(.*)', self._uri)
        if match:
            host_config.set_server(match.group(1))
            host_config.set_port(int(match.group(2)))
            host_config.get_exchange().set_name(match.group(3))
            host_config.get_queue().set_name(match.group(4))
            host_config.get_queue().add_routing_key(match.group(4))
        else:
            raise NameError("Invalid host name", self._uri)
