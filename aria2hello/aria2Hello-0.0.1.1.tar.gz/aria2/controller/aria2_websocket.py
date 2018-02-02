# -*- coding: utf-8 -*-
import websocket
import threading
from aria2.controller.mq_client import MQClient
from aria2_api import Aria2Api


class Aria2WebSocket(object):
    """处理Aria2的websocket连接"""
    ws = None
    client = None
    aria2_api = None
    
    def __init__(self, ip, port, password, device_id):
        self.ip = ip
        self.port = port
        self.password = password
        self.device_id = device_id
    
    def connect_aria2(self):
        """websocket连接aria2"""
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp("ws://%s:%s/jsonrpc" % (self.ip, self.port),
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.on_message = self.on_message
        ws.run_forever()
    
    def on_message(self, ws, message):
        """websocket收到通知"""
        
        def run(client, ws, message):
            print "收到通知：%s" % message
            client.publish('0', message)
        
        t1 = threading.Thread(target=run, name='Receiver', args=(self.client, ws, message))
        t1.start()
    
    def on_error(self, ws, error):
        """websocket连接错误"""
        print "连接aria2 rpc接口失败 error. {} ".format(error)
    
    def on_close(self, ws):
        "websocket关闭"
        print "websocket关闭"
        if self.client is not None:
            self.client.close()
    
    def on_open(self, ws):
        """websocket打开"""
        self.client = MQClient(device_id=self.device_id)
        self.client.connect()
        self.aria2_api = Aria2Api(self.ip, self.port, self.password)
        self.client.set_aria2_api(self.aria2_api)
