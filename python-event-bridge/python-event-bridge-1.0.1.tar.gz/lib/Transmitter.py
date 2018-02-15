from lib.NATSTransmitter import NATSTransmitter


class Transmitter:

    @classmethod
    async def create(cls, server):
        self = Transmitter()
        self.server = server.upper()
        if server == "NATS":
            self.connection = NATSTransmitter()
            await self.connection.connect()
        else:
            self.connection = NATSTransmitter()
            await self.connection.connect()
        return self

    async def subscribe(self, subject, message_handler):
        await self.connection.subscribe(subject, message_handler)

    async def unsubscribe(self, subject):
        await self.connection.unsubscribe(subject)

    async def publish(self, subject, message):
        await self.connection.publish(subject, message)

    async def close(self):
        await self.connection.close()






