import asyncio
import multiprocessing
from bubot.Action import Action
from bubot import BujectHelper
from bubot.Buject import Buject
from bubot.BujectError import UserError, BujectError


class BasicWorker(Buject):
    def __init__(self, **kwargs):
        Buject.__init__(self, **kwargs)
        self.type = 'worker'

    def run(self):
        # self.log("Start worker {name}".format(name=self.name))
        try:
            self.loop = asyncio.get_event_loop()
            self.init()
            self.loop.run_until_complete(self.handler())
            self.on_close()
        except BujectError as e:
            self.set_param('buject_status', 'error')
            self.set_param('buject_status_detail', e.to_json())
            print('error run worker {0} - {1}'.format(self.id, str(e)))
            pass
        except Exception as e:
            _error = BujectError(e, action_name='{0}.run'.format(self.get_uuid()))
            self.set_param('buject_status', 'error')
            self.set_param('buject_status_detail', _error.to_json())
            print('error run worker {0} - {1}'.format(self.get_uuid(), str(e)))
            pass

    async def on_ready(self):
        await super().on_ready()
        await asyncio.wait_for(self.broker.subscribe_ready, self.broker.timeout)
        await self.send_event('worker_ready', {'worker_id': self.id})

    async def action_run_buject(self, data):
        res = Action('Worker.action_run_buject')
        res.result = res.add_stat(await BujectHelper.run_buject(data['buject_id'], data['config'], self, True))
        return res.set_end()

    async def action_close_buject(self, data):
        res = Action('Worker.action_close_buject')
        pass
        return res.set_end()


class Worker(BasicWorker, multiprocessing.Process):
    def __init__(self, worker_id, **kwargs):
        BasicWorker.__init__(self, **kwargs)
        multiprocessing.Process.__init__(self)
        self.id = worker_id
        self.config = BujectHelper.config_to_simple_dict(
            BujectHelper.read_config(BujectHelper.get_path_default_config(self.type)))
        pass

    # def run(self):
    #     # self.log("Start worker {name}".format(name=self.name))
    #     try:
    #         self.loop = asyncio.get_event_loop()
    #         self._init()
    #         self.loop.run_until_complete(self.handler())
    #         self.on_close()
    #     except BujectError as e:
    #         self.set_param('buject_status', 'error')
    #         self.set_param('buject_status_detail', e.to_json())
    #         print('error run worker {0} - {1}'.format(self.id, str(e)))
    #         pass
    #     except Exception as e:
    #         self.set_param('buject_status', 'error')
    #         self.set_param('buject_status_detail', BujectError(str(e)).to_json())
    #         print('error run worker {0} - {1}'.format(self.id, str(e)))
    #         pass
    # async def on_init(self):
    #     await super().on_init()
    #     for elem in self.config['buject']:
    #         await BujectHelper.run_buject(elem, self.config['buject'][elem], self)

            # async def on_run(self):
            #     await asyncio.sleep(5)
            # print(self.get_uuid())


    # async def request_stop_buject(self, message):
    #     del self.buject[message['param']]
    #
        # def __str__(self):
        #     return self.id

        # async def check_close(self):
        #     if not self.buject or self.param['buject_status'] == 'close':  # выключаем если ничего не выполняется
        #         self.param['buject_status'] = ''
        #         await self.send_buject_param()
        #         return True
        #     return False


class WorkerQueue(BasicWorker, multiprocessing.Process):
    def __init__(self, worker_id, queue, **kwargs):
        kwargs['id'] = worker_id
        BasicWorker.__init__(self, **kwargs)
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.type = 'queue'
        self.buject = None

    def get_uuid(self):
        return '{0}_{1}_{2}'.format(self.type, self.queue, self.id)

    async def handler(self):
        await self.get_broker()
        await asyncio.gather(self.broker.handler_msg(), self.broker.handler_queue())
