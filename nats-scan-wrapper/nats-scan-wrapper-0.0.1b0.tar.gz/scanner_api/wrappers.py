import asyncio
import logging
import nats.aio.client
import json
from nats.aio.errors import ErrNoServers, ErrConnectionClosed

logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)


class scanner_wrapper:
    config = {
        # Count packets from queue received at a time
        # "data_pack_size": 1,
    }

    def __init__(self, **kwargs):
        if "name" in kwargs:
            nats.aio.client.__version__ = kwargs["name"]
        else:
            raise Exception("No name for module")
        self.config.update(kwargs)

    def configure(self, **kwargs):
        self.config.update(kwargs)

    async def _run(self, loop, func):
        nc = nats.aio.client.Client()

        @asyncio.coroutine
        def disconnected_cb():
            logging.info("Got disconnected!")

        @asyncio.coroutine
        def reconnected_cb():
            # See who we are connected to on reconnect.
            logging.info("Got reconnected to " + str(nc.connected_url.netloc))

        @asyncio.coroutine
        def error_cb(e):
            logging.error("There was an error: " + str(e))

        @asyncio.coroutine
        def closed_cb():
            logging.info("Connection is closed")

        # Configuring nats
        options = {
            # Setup pool of servers from a NATS cluster.
            "servers": self.config['nats'],
            "io_loop": loop,
            # Will try to connect to servers in order of configuration,
            # by defaults it connect to one in the pool randomly.
            "dont_randomize": True,
            # Optionally set reconnect wait and max reconnect attempts.
            # This example means 10 seconds total per backend.
            "max_reconnect_attempts": 5,
            "reconnect_time_wait": 10,
            # Setup callbacks to be notified on disconnects and reconnects
            "disconnected_cb": disconnected_cb,
            "reconnected_cb": reconnected_cb,
            # Setup callbacks to be notified when there is an error
            # or connection is closed.
            "error_cb": error_cb,
            "closed_cb": closed_cb
        }

        while not nc.is_connected:
            try:
                await nc.connect(**options)
                logging.info("Connected to NATS.")
                logging.info("Started module named '{name}'.".format(
                    name=self.config["name"]))
            except ErrNoServers as e:
                # Could not connect to any server in the cluster.
                logging.error(e)

        @asyncio.coroutine
        async def message_handler(msg):
            source = msg.subject
            new_pipeline = ".".join(source.split(".")[1:])
            data = msg.data.decode()
            logging.info("Received from '{subject}': {data}".format(
                subject=source, data=data))
            # Scanning (start function)
            try:
                logging.info("Starting '{name}'".format(
                    name=self.config["name"]))
                result = func(source, json.loads(data))
                if result:
                    if new_pipeline:
                        try:
                            for r in result:
                                json_r = json.dumps(r)
                                await nc.publish(new_pipeline, json_r.encode())
                                logging.info("Result: {result} \n Was sent to '{pipeline}'".format(
                                    result=json_r, pipeline=new_pipeline))
                        except ErrConnectionClosed:
                            logging.error("Connection closed prematurely.")
                    else:
                        for r in result:
                            json_r = json.dumps(r)
                            logging.info("Result: {result} \n Wasn't sent! End of pipeline!".format(
                                result=json_r))
                else:
                    logging.info("Result is empty!")

            except Exception as e:
                logging.error("Error in {name} worker function".format(
                    name=self.config["name"]))
                logging.error(e)
                logging.error(source)
                logging.error(data)

        if nc.is_connected:
            # Simple publisher and async subscriber via coroutine.
            await nc.subscribe(
                str(self.config["name"]) + ".>",
                self.config["name"],
                cb=message_handler
            )
            await nc.subscribe(
                str(self.config["name"]),
                self.config["name"],
                cb=message_handler
            )
            while True:
                await asyncio.sleep(3, loop=loop)

            await nc.close()

    def run(self, func):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run(loop, func))
        loop.close()
