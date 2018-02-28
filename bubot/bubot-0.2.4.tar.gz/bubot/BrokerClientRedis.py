import asyncio
from datetime import datetime
import asyncio_redis
from bson import json_util
from bubot import BujectHelper
from bubot.Action import Action
from bubot.BrokerClient import BrokerClient
from bubot.BujectError import BujectError, UserError


class BrokerClientRedis(BrokerClient):
    def __init__(self, buject):
        super().__init__(buject)
        self.host = buject.bubot.get('broker_host', 'localhost')
        self.port = buject.bubot.get('broker_port', 6379)
        self.db = buject.bubot.get('broker_db', 0)
        self.timeout = buject.bubot.get('broker_timeout', 20)
        self.pool_size = buject.bubot.get('broker_pool_size', 3)
        self.subscribe_list = None
        self.pubsub = None
        self.redis = None
        self.lock_redis = None

        # self.param = {}
        # self.status = {}

    async def init(self):
        res = Action('BubotClientRedis._init')
        try:
            self.lock_redis = asyncio.Lock()
            self.redis = await asyncio.wait_for(
                asyncio_redis.Pool.create(host=self.host, port=int(self.port), db=int(self.db),
                                          poolsize=self.pool_size),
                self.timeout)
            return res
        except asyncio.futures.TimeoutError:
            raise TimeoutError('Redis.Connection({0}:{1}))'.format(self.host, self.port, self.db))
        except Exception as e:
            raise BujectError(e, action=res)

    # async def handler(self):
    #     pass

    # async def publish(self, channel, message):
    #     await self.redis.publish(channel, message)

    # async def next_published(self):
    #     return await self.subscriber.next_published()

    async def read_buject_config(self, buject_name):
        result = await self.redis.hget('bubot_config', buject_name)
        if not result:
            raise UserError('buject config not found', buject_name)
        return json_util.loads(result)

    async def write_buject_config(self, buject_name, buject_config):
        return await asyncio.wait_for(
            self.redis.hset('bubot_config', buject_name, json_util.dumps(buject_config)),
            self.timeout)

    async def check_redis(self):
        pass

    async def handler_msg(self):
        await self.check_redis()
        self.subscribe_list = await self.get_subscribe_list()
        if not await self.subscribe(self.subscribe_list):
            return False
        self.subscribe_ready.set_result(True)
        while True:
            msg_redis = await self.pubsub.next_published()
            if msg_redis:
                res = Action('handler_msg')
                try:
                    msg = self.msg_class().init_from_json(msg_redis.value)
                    try:
                        res.add_stat(await getattr(self.buject, 'handler_{0}'.format(msg.type))(msg))
                    except BujectError as e:
                        res.error = e.to_json()
                    except Exception as e:
                        res.error = BujectError(e, action=res).to_json()
                    finally:
                        if msg.type == 'request':
                            response = msg.get_response(res)
                            await self.send_msg(response)
                except Exception as e:
                    await self.buject.error('{0}.bad format redis msg: {1}'.format(self.buject.id, e))

    async def handler_queue(self):
        while True:
            msg_redis = await self.redis.brpop(['queue_{0}'.format(self.buject.queue)])
            if msg_redis:
                res = Action('handler_queue')
                try:
                    msg = self.msg_class().init_from_json(msg_redis.value)
                    try:
                        config = await self.read_buject_config(msg.receiver)
                        buject_class = BujectHelper.get_buject(config['param']['buject'])
                        buject = buject_class(id=msg.receiver[7:], config=config, bubot=self.buject.bubot, db=self.db,
                                              loop=self.buject.loop, broker=self)
                        buject.init()
                        res.result = res.add_stat(await getattr(buject, 'handler_{0}'.format(msg.type))(msg))
                    except BujectError as e:
                        _error = BujectError(e, msg.dump(), action=res)
                        res.error = _error.to_json()
                    except Exception as e:
                        _error = BujectError(e, msg.dump(), action=res)
                        res.error = _error.to_json()
                    finally:
                        if msg.type == 'request':
                            response = msg.get_response(res.dump())
                            await self.send_msg(response)
                except Exception as e:
                    await self.buject.error('handler_queue: bad format redis msg', str(e))

    async def subscribe(self, subscribe_list=None):
        if not subscribe_list:
            if not self.subscribe_list:
                return False
        await self.check_redis()
        with (await self.lock_redis):
            if not self.pubsub:
                self.pubsub = await asyncio.wait_for(self.redis.start_subscribe(), 1)
            await self.pubsub.subscribe(self.subscribe_list)
        return True

    async def send_msg(self, msg):
        res = Action('send_msg')
        return res.set_end(await self.redis.publish(msg.receiver, msg.dump()))
        pass

    async def add_to_queue(self, queue_name, msg):
        res = Action('add_to_queue')
        if not queue_name:
            raise UserError('queue_name not defined', action=res)
        if not msg.receiver:
            raise UserError('receiver not defined', action=res)
        await self.redis.lpush("queue_{0}".format(queue_name), [msg.dump(), ])

