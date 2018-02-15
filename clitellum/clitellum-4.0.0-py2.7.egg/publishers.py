from clitellum.core import serialization
from clitellum.core.bus import MessageBuilder
from clitellum.endpoints import gateways
from clitellum.server import Identification

__author__ = 'Sergio'


def create_agent_from_config(cfg):
    identification = Identification(cfg['identification']['id'], cfg['identification']['type'])
    sg = gateways.CreateSenderFromConfig(cfg["sender_gateway"])
    return Publisher(identification, sg)


class Publisher:

    def __init__(self, identification, sender_gateway):
        self._identification = identification
        self._senderGateway = sender_gateway
        self._senderGateway.connect()

    @property
    def identification(self):
        return self._identification

    def publish(self, message, key, context=None):
        message_bus = MessageBuilder.create() \
                        .set_body(message) \
                        .set_type(key) \
                        .set_context(context) \
                        .set_service(self.identification) \
                        .build()

        message_serialized = serialization.dumps(message_bus)
        self._senderGateway.send(message_serialized, key)

    def __del__(self):
        self._senderGateway.close()
