# author = sbermudel
# package description
from clitellum.core import compressors
from clitellum.endpoints.channels import reconnectiontimers
from clitellum.endpoints.channels.amqp.channels import OutBoundAmqpChannel, InBoundAmqpChannel
from clitellum.endpoints.channels.basechannels import Channel
from clitellum.endpoints.channels.tcpsocket import OutBoundChannelTcp, InBoundChannelTcp
from clitellum.endpoints.channels.zeromq import OutBoundChannelZeroMq, InBoundChannelZeroMq
from clitellum.endpoints.channels.amqp.builders import AmqpChannelBuilderFactory


## Crea un canal a partir de una configuracion
# { type : 0Mq,
#   timer : Logarithmic,
#   host : tcp://server:8080,
#   maxReconnections : 20,
#   compressor: { type="gzip", compressionLevel: 9 },
#   useAck : False}
def CreateOutBoundChannelFromConfig(config):
    if 'timer' in config:
        timer = reconnectiontimers.CreateTimerFormType(config["timer"])
    else:
        timer = reconnectiontimers.CreateConstantTimer()

    if 'compressor' in config:
        compressor = compressors.CreateCompressorFromConfig(config["compressor"])
    else:
        compressor = compressors.DefaultCompressor()

    maxReconnections = Channel.MAX_RECONNECTIONS
    if not config.get("maxReconnections") is None:
        maxReconnections = int(config.get("maxReconnections"))

    useAck = False
    if not config.get("useAck") is None:
        useAck = bool(config.get("useAck"))

    user = 'guest'
    password = 'guest'

    if 'user' in config:
        user = config['user']

    if 'password' in config:
        password = config['password']

    if config.get("type").lower() == "0mq":
        channel = OutBoundChannelZeroMq(config["host"], reconnectionTimer=timer,
                                        maxReconnections=maxReconnections, compressor=compressor)
    elif config.get("type").lower() == "tcp":
        channel = OutBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                     maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    elif config.get("type").lower() == "amqp":

        builder = AmqpChannelBuilderFactory.create_out_bound_builder()
        builder.set_uri(config["host"]) \
                .set_compressor(compressor) \
                .set_max_recconections(maxReconnections) \
                .set_reconnection_timer(timer) \
                .set_credentials(user, password) \
                .set_use_ack(useAck)

        if 'exchange_type' in config:
            if config['exchange_type'] == 'direct':
                builder.set_direct_exchange()
            else:
                builder.set_topic_exchange()
        else:
            builder.set_topic_exchange()

        if 'create_exchange' in config:
            builder.set_create_exchange(config['create_exchange'])
        else:
            builder.set_create_exchange(True)

        channel = builder.build()

    elif config.get("type").lower() == "custom":
        factory = _get_class(config["factory"])()
        channel = factory.create_from_cfg(config, timer, compressor, maxReconnections)

    else:
        channel = OutBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                     maxReconnections=maxReconnections, compressor=compressor, useAck=useAck)
    return channel


def CreateInBoundChannelFromConfig(config):
    if 'timer' in config:
        timer = reconnectiontimers.CreateTimerFormType(config["timer"])
    else:
        timer = reconnectiontimers.CreateConstantTimer()

    if 'compressor' in config:
        compressor = compressors.CreateCompressorFromConfig(config["compressor"])
    else:
        compressor = compressors.DefaultCompressor()

    maxReconnections = Channel.MAX_RECONNECTIONS
    if not config.get("maxReconnections") is None:
        maxReconnections = int(config.get("maxReconnections"))

    useAck = False
    if 'useAck' in config:
        useAck = bool(config.get("useAck"))

    user = 'guest'
    password = 'guest'

    if 'user' in config:
        user = config['user']

    if 'password' in config:
        password = config['password']        

    maxChannelThread = 5
    if 'maxChannelThread' in config:
        maxChannelThread = config['maxChannelThread']

    if config.get("type").lower() == "0mq":
        channel = InBoundChannelZeroMq(config["host"], reconnectionTimer=timer,
                                       maxReconnections=maxReconnections, compressor=compressor)
    elif config.get("type").lower() == "tcp":
        channel = InBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                    maxReconnections=maxReconnections, \
                                    compressor=compressor, useAck=useAck)
    elif config.get("type").lower() == "amqp":

        builder = AmqpChannelBuilderFactory.create_in_bound_builder()
        builder.set_uri(config["host"]) \
                .set_compressor(compressor) \
                .set_max_recconections(maxReconnections) \
                .set_reconnection_timer(timer) \
                .set_credentials(user, password) \
                .set_use_ack(useAck) \
                .set_max_threads(maxChannelThread) \

        if 'exchange_type' in config:
            if config['exchange_type'] == 'direct':
                builder.set_direct_exchange()
            else:
                builder.set_topic_exchange()
        else:
            builder.set_topic_exchange()
                
        if 'create_exchange' in config:
            builder.set_create_exchange(config['create_exchange'])
        else:
            builder.set_create_exchange(True)

        if 'create_queue' in config:
            builder.set_create_queue(config['create_queue'])
        else:
            builder.set_create_queue(True)

        channel = builder.build()

    elif config.get("type").lower() == "custom":
        factory = _get_class(config["factory"])()
        channel = factory.create_from_cfg(config, timer, compressor, maxReconnections)

    else:
        channel = InBoundChannelTcp(config["host"], reconnectionTimer=timer,
                                    maxReconnections=maxReconnections, \
                                    compressor=compressor, useAck=useAck)
    return channel


def _get_class(class_name):
    parts = class_name.split('.')
    module = ".".join(parts[:-1])
    module_obj = __import__(module)
    for comp in parts[1:]:
        module_obj = getattr(module_obj, comp)
    return module_obj


class CustomFactoryBase:
    def __init__(self):
        pass

    def create_from_cfg(self, cfg, reconnectionTimer, compressor, maxReconnections):
        pass
