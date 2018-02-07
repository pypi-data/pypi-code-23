import asyncio

class client():
    def __init__(self):
        self.reader = None
        self.writer = None
        self.received = None
        self.managed = True

    async def connect(self,loop, serverHost='dashboard.nodewire.org', failed=None):
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(serverHost, 10001, loop=loop)
                while True:
                    try:
                        data = await self.reader.readline()
                        if len(data)==0 and self.received:
                            self.received('disconnected')
                            break
                        if self.received:
                            try:
                                self.received(data.decode().strip())
                            except Exception as ex1:
                                print(str(ex1))
                                if not self.managed: raise
                    except ConnectionError as ex: # todo use specified exception type
                        print(str(ex))
                        if self.received:
                            self.received('disconnected')
                        break
                print('Close the socket')
                self.writer.close()
                self.writer = None
                await asyncio.sleep(10)
                print('trying to reconnect...')
            except Exception as Ex: # todo get the relevant exceptions: TimeoutError
                print('failed to connect')
                if failed!=None:
                    failed(serverHost)
                    break
                await asyncio.sleep(30)
                print('trying to reconnect...')

    def close_connection(self):
        self.writer.close()
        self.writer = None

    async def sendasync(self, message):
        while(self.writer==None): await asyncio.sleep(1)
        self.writer.write(message.encode())

    def send(self, message):
        self.writer.write(message.encode())

if __name__ == '__main__':
    c = client()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(c.connect(loop))
    except KeyboardInterrupt:
        pass
    loop.close()