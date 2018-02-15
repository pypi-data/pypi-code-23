
from clitellum.core import compressors
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.basechannels import Channel
from clitellum.endpoints.channels.amqp.channels import InBoundAmqpChannel, OutBoundAmqpChannel
from clitellum.endpoints.channels.amqp.configuration import AmqpHostConfigurationBuilder

class AmqpChannelBuilderFactory(object):
    '''
    Factoria de builders
    '''
    @classmethod
    def create_in_bound_builder(cls):
        '''
        Devuelve una instancia del builder de canales de entrada amqp
        '''
        reconnection_timer = reconnectiontimers.CreateLogarithmicTimer()
        amqp_host_builder = AmqpHostConfigurationBuilder.create()
        compressor = compressors.NoCompressor()

        return InBoundAmqpChannelBuilder(reconnection_timer, amqp_host_builder, compressor)

    @classmethod
    def create_out_bound_builder(cls):
        '''
        Devuelve una instancia del builder de canales de salida amqp
        '''
        reconnection_timer = reconnectiontimers.CreateLogarithmicTimer()
        amqp_host_builder = AmqpHostConfigurationBuilder.create()
        compressor = compressors.NoCompressor()

        return OutBoundAmqpChannelBuilder(reconnection_timer, amqp_host_builder, compressor)
    

class AmqpChannelBuilder():
    '''
    Constructor de canales Amqp
    '''
    def __init__(self, reconnection_timer, amqp_host_builder, compressor):
        self._reconnection_timer = reconnection_timer
        self._amqp_host_builder = amqp_host_builder
        self._compressor = compressor
        self._max_reconnections = Channel.MAX_RECONNECTIONS


    def set_uri(self, uri):
        '''
        Establece la uri del servidor de amqp
        '''
        self._amqp_host_builder.set_uri(uri)
        return self

    def set_direct_exchange(self):
        '''
        Establece el tipo direct en el exchange
        '''
        self._amqp_host_builder.set_direct_exchange()
        return self

    def set_max_recconections(self, max_reconnections):
        '''
        Establece el numero maximas de reconexiones contra el servidor de amqp
        por defecto son infinitas
        '''
        self._max_reconnections = max_reconnections
        return self

    def set_topic_exchange(self):
        '''
        Establece el tipo topic en el exchange
        '''
        self._amqp_host_builder.set_topic_exchange()
        return self

    def set_create_exchange(self, value):
        '''
        Establece que se cree el exchange durante la conexion
        '''
        self._amqp_host_builder.set_create_exchange(value)
        return self

    def set_create_queue(self, value):
        '''
        Establece que se cree el cola durante la conexion
        '''
        self._amqp_host_builder.set_create_queue(value)
        return self

    def set_credentials(self, user, password):
        '''
        Establece la credenciales de conexion
        '''
        self._amqp_host_builder.set_credentials(user, password)
        return self

    def set_use_ack(self, value):
        '''
        Establece si se debe usar ack en la conexion
        '''
        self._amqp_host_builder.set_use_ack(value)
        return self

    def set_prefetch_count(self, count):
        '''
        Establece el prefetch count del amqp
        '''
        self._amqp_host_builder.set_prefetch_count(count)
        return
    
    def set_prefetch_size(self, size):
        '''
        Establece el prefetch size del amqp
        '''
        self._amqp_host_builder.set_prefetch_size(size)
        return self

    def set_reconnection_timer(self, reconnection_timer):
        '''
        Establece el temporizador de la reconexion
        por defecto Logaritmico
        '''
        self._reconnection_timer = reconnection_timer
        return self

    def set_compressor(self, compressor):
        '''
        Establece el compresor del endpoint
        '''
        self._compressor = compressor
        return self

    def build(self):
        '''
        Crear una instancia de un canal Amqp
        '''
        raise NotImplementedError()

class OutBoundAmqpChannelBuilder(AmqpChannelBuilder):
    '''
    Constructor de canales de salida ampp
    '''
    def __init__(self, reconnection_timer, amqp_host_builder, compressor):
        AmqpChannelBuilder.__init__(self, reconnection_timer, amqp_host_builder, compressor)

    def build(self):
        amqp_host_conf = self._amqp_host_builder.set_is_out_bound().build()
        channel = OutBoundAmqpChannel(amqp_host_conf, self._reconnection_timer, \
                                    self._max_reconnections, \
                                    self._compressor)
        return channel


class InBoundAmqpChannelBuilder(AmqpChannelBuilder):
    '''
    Constructor de canales de entrada amqp
    '''

    def __init__(self, reconnection_timer, amqp_host_builder, compressor):
        AmqpChannelBuilder.__init__(self, reconnection_timer, amqp_host_builder, compressor)
        self._recception_timeout = 10
        self._max_threads = 1

    def set_timeout(self, timeout):
        '''
        Establece el timeout del bucle de recepcion, por defecto son 10 segundos
        '''
        self._recception_timeout = timeout
        return self

    def set_max_threads(self, max_threads):
        '''
        Establece el numero de hilos de extraccion
        '''
        self._max_threads = max_threads
        return self


    def build(self):
        '''
        Crear una instancia de un canal Amqp
        '''
        amqp_host_conf = self._amqp_host_builder.set_is_in_bound().build()
        channel = InBoundAmqpChannel(amqp_host_conf, self._reconnection_timer, \
                                    self._max_reconnections, self._recception_timeout, \
                                    self._compressor, self._max_threads)
        return channel
