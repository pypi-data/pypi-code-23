import asyncio
from datetime import datetime
from bubot.Action import Action
import uuid
from bson import json_util


class BrokerClient:
    def __init__(self, buject):
        self.buject = buject
        self.msg_class = BrokerMsg
        self.timeout = buject.bubot.get('broker_timeout', 20)
        self.waiting_response = {}
        self.subscribe_ready = asyncio.Future()

    async def init(self):
        res = Action('BubotClientRedis._init')
        return res.set_end()
        pass

    async def get_subscribe_list(self):
        subscribe_list = self.buject.config.get('subscribe_list', [])
        subscribe_list.append(self.buject.get_uuid())
        return subscribe_list

    def get_buject_for_worker(self, worker_id):
        res = {}
        for buject_id in self.buject.config['buject']:
            try:
                if self.buject.config['buject'][buject_id]['param']['worker_id'] == worker_id:
                    res[buject_id] = self.buject.config['buject'][buject_id]
            finally:
                pass
        return res

    def get_worker_param(self, worker_id):

        return {'buject': self.get_buject_for_worker(worker_id)}

    def add_waiting_response(self, _uuid):
        self.waiting_response[_uuid] = {
            'future': asyncio.Future(),
            'begin': datetime.now()
        }
        return self.waiting_response[_uuid]['future']


class CloseBrokerClient(Exception):
    pass


class BrokerMsg:
    def __init__(self, **kwargs):
        self.sender = None
        self.receiver = None
        self.topic = None
        self.data = None
        self.uuid = None
        self.type = None  # msg, request, response, error
        self.init(kwargs)
        pass

    def init(self, data):
        self.sender = data.get('sender', None)
        self.receiver = data.get('receiver', 'bubot')
        self.type = data.get('type', 'msg')
        self.topic = data.get('topic', 'console')
        self.data = data.get('data', None)
        self.uuid = data.get('uuid', str(uuid.uuid4()))
        return self

    def __str__(self):
        return 'sender: {0}, receiver: {1}, topic:{2}'.format(self.sender, self.receiver, self.topic)

    # async def handler_msg(self):
    #     return None
    #
    # async def read_buject_config(self, buject_id):
    #     pass

    def get_response(self, data):
        _resp = self.__class__()
        _resp.sender = self.receiver
        _resp.receiver = self.sender
        _resp.uuid = self.uuid
        _resp.type = 'response'
        _resp.data = data
        return _resp

    def init_from_json(self, json_data):
        return self.init(json_util.loads(json_data))

    # def get_queue_broker(self, broker, broker_param):
    #     pass
    #
    # def get_publish_broker(self, broker, broker_param):
    #     pass
    #
    # def add_to_queue(self, queue, broker):
    #     pass
    #
    # def publish(self, broker):
    #     pass
    #
    # def handle_publish_msg(self, worker):
    #     pass

    def dump(self):
        return json_util.dumps({
            'sender': self.sender,
            'receiver': self.receiver,
            'type': self.type,
            'topic': self.topic,
            'data': self.data,
            'uuid': self.uuid
        }, ensure_ascii=False)
