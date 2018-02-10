from models import Controls


class BotControlUpdate:
    def __init__(self, socketId, botId, controls: Controls):
        self.controls = controls
        self.botId = botId
        self.socketId = socketId
