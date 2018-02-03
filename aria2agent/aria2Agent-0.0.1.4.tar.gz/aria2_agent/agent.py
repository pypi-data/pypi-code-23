# -*- coding: utf-8 -*-

from aria2_agent.mq.mq_client import MQClient
from aria2_agent.api.aria2_api import Aria2Api
from aria2_agent.websocket_rpc.aria2_websocket import Aria2WebSocket
import json


class Agent(object):
    """代理"""
    mq_client = None
    aria2_api = None
    aria2_websocket = None
    
    def __init__(self, rpc_host, rpc_port, rpc_secret, device_id):
        self.rpc_host = rpc_host
        self.rpc_port = rpc_port
        self.rpc_secret = rpc_secret
        self.device_id = device_id
        self.mq_client = MQClient(device_id)
        self.mq_client.on_close = self.close
        self.mq_client.on_mq_message = self.on_mq_message
        
        self.aria2_api = Aria2Api(self.rpc_host, self.rpc_port, self.rpc_secret)
        self.aria2_websocket = Aria2WebSocket(self.rpc_host, self.rpc_port, self.rpc_secret, self.device_id)
        self.aria2_websocket.on_close = self.close
        self.aria2_websocket.on_message = self.on_websocket_message
    
    def connect(self):
        self.mq_client.connect()
        self.aria2_websocket.connect()
    
    def close(self):
        """关闭"""
        if self.mq_client:
            self.mq_client.close()
        if self.aria2_websocket:
            self.aria2_websocket.close()
    
    def on_websocket_message(self, message):
        """收到websocket消息"""
        self.mq_client.publish('0', message)
    
    def on_mq_message(self, client, userdata, msg):
        """收到服务器消息"""
        msg_obj = json.loads(str(msg.payload))
        msg_id = msg_obj['msgId']
        method = msg_obj['method']
        args = msg_obj['args']
        self.aria2_api.invoke(msg_id=msg_id, method=method, args=args, callback=self.mq_client.publish)
