class IdentificationBot:
    def __init__(self, botId, botSecret, connection):
        self.connection = connection
        self.botSecret = botSecret
        self.botId = botId
