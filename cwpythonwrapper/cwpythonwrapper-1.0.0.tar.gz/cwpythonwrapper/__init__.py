__all__ = [
    'CwPythonWrapper'
]

from socketIO_client_nexus import SocketIO, LoggingNamespace
import json

from .BotControlUpdate import BotControlUpdate
from .IdentificationBot import IdentificationBot
from .models.State import State
from collections import namedtuple


class CwPythonWrapper:
    def __init__(self, botId, botSecret, tick):
        self.botId = botId,
        self.botSecret = botSecret,
        self.tick = tick
        self.socketIO.on("do-identification", self.on_do_identification)
        self.socketIO.on('identification-successful', self.on_identification_successful)
        self.socketIO.on('identification-bot-successful', self.identification_bot_successful)
        self.socketIO.on('identification-bot-failed', self.identification_bot_failed)
        self.socketIO.on('state', self.state)
        self.socketIO.wait()

    socketIO = SocketIO('localhost', 8080, LoggingNamespace)

    def on_do_identification(self, *args):
        self.socketIO.emit("identification", "VALID")

    def on_identification_successful(self, args):
        self.id = args
        identificationBot = IdentificationBot(self.botId[0], self.botSecret[0], self.id)
        self.socketIO.emit("identification-bot", json.dumps(identificationBot.__dict__))

    def identification_bot_successful(self, *args):
        print('bot authenticated')

    def identification_bot_failed(self, *args):
        print(args)

    def _json_object_hook(self, d):
        return namedtuple('X', d.keys())(*d.values())

    def json2obj(self, data):
        return json.loads(data, object_hook=self._json_object_hook)

    def state(self, args):
        state = State.fromState(self.json2obj(json.dumps(args)))
        controls = self.tick(state)
        bot_control_update = BotControlUpdate(self.id, self.botId[0], controls)
        self.socketIO.emit('bot-control-update', json.dumps(bot_control_update.__dict__))
