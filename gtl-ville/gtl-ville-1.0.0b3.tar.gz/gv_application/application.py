#!/usr/bin/env python3


import aioredis
import asyncio
import functools
import json
import traceback

from gv_application.logger import GVLogger


class GVApplication:

    def __init__(self, logname, logfile):
        self.logger = GVLogger(parent=logname, logfile=logfile)
        self.logger.debug('Starting application...')

        self.loop = None
        self.redispool = None

    def init_in_thread(self, loop, redisaddr):
        self.__set_loop(loop)
        self.__set_redispool(redisaddr)
        self.__run()

    def __set_loop(self, loop):
        self.loop = loop
        asyncio.set_event_loop(self.loop)

    def __set_redispool(self, redisaddr):
        if self.loop is None:
            self.logger.error('No event loop. return.')
            return

        try:
            self.redispool = self.loop.run_until_complete(
                asyncio.ensure_future(aioredis.create_redis_pool(redisaddr, encoding='utf-8', loop=self.loop,
                                                                 minsize=5, maxsize=10))
            )
            self.logger.debug('Connected to Redis server.')
        except asyncio.TimeoutError:
            self.logger.warning('Unable to connect to the Redis server.')

    def __run(self):
        if self.loop is None:
            self.logger.error('No event loop. return.')
            return

        self.loop.call_soon_threadsafe(functools.partial(self.logger.info, 'Application started.'))
        try:
            self.loop.run_forever()
        finally:
            self.logger.debug('Event loop stopped.')
            self.logger.debug('Closing event loop...')
            self.loop.close()
            self.logger.debug('Event loop closed.')
        self.logger.info('Application stopped.')

    async def add_callback(self, channelname, callback):
        if self.redispool is not None:
            channel = (await self.redispool.subscribe(channelname))[0]
            while await channel.wait_message():
                data = (await channel.get_json()).get('data')
                asyncio.ensure_future(self.loop.run_in_executor(None, functools.partial(callback, data)))
            self.logger.warning('Application has stopped to listen Redis channel:' + str(channelname))

    async def publish(self, channelname, data):
        if self.redispool is not None:
            message = json.dumps({'data': data}, separators=(',', ':'), default=self.__serialiaze_json)
            asyncio.ensure_future(self.redispool.publish(channelname, message))

    def stop(self):
        self.logger.debug('Stopping application...')
        if self.redispool is not None:
            self.__close_redis_pool()
        self.__stop_close_loop()

    def __close_redis_pool(self):
        self.logger.debug('Closing Redis connections...')
        self.redispool.close()
        self.logger.debug('Redis connections closed.')

    def __stop_close_loop(self):
        self.logger.debug('Stopping event loop...')
        self.loop.stop()

    def __serialiaze_json(self, obj):
        try:
            return obj.isoformat()
        except ValueError:
            self.logger.error('Unable to serialize obj: ' + str(obj))
            self.logger.error(traceback.format_exc())
            return None
