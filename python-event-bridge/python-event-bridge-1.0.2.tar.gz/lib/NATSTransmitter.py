from nats.aio.client import Client as NATS
from lib.BaseTransmitter import BaseTransmitter


class NATSTransmitter(BaseTransmitter):

    def __init__(self):
        print("something good")
        self.nats = NATS()
        self.servers = ["nats://0.0.0.0:4222"]
        super(NATSTransmitter, self).__init__()

    async def connect(self):
        print("connect")
        return await self.nats.connect(servers=self.servers)

    async def subscribe(self, subject, message_handler):
        print("subscribe", subject)
        return await self.nats.subscribe(subject, cb=message_handler)

    async def unsubscribe(self, ssid):
        print("unsubscribe", ssid)
        return await self.nats.unsubscribe(ssid)

    async def publish(self, subject, message):
        print("publish", subject,  message)
        return await self.nats.publish(subject, message)

    async def close(self):
        print("close")
        return await self.nats.close()