# -*- coding: utf-8 -*-
import threading

import websocket


class Aria2WebSocket(object):
    """处理Aria2的websocket连接"""
    ws = None
    on_close = None
    on_message = None
    
    def __init__(self, ip, port, password, device_id):
        self.ip = ip
        self.port = port
        self.password = password
        self.device_id = device_id
    
    def connect(self):
        """websocket连接aria2"""
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp("ws://%s:%s/jsonrpc" % (self.ip, self.port),
                                         on_error=self.on_ws_error,
                                         on_close=self.on_ws_close)
        self.ws.on_open = self.on_ws_open
        self.ws.on_message = self.on_ws_message
        self.ws.run_forever()
    
    def on_ws_message(self, ws, message):
        """websocket收到通知"""
        
        def run(on_message, ws, message):
            print "收到通知：%s" % message
            on_message(message)
        
        t1 = threading.Thread(target=run, name='Receiver', args=(self.on_message, ws, message))
        t1.start()
    
    def on_ws_error(self, ws, error):
        """websocket连接错误"""
        print "连接aria2 rpc接口失败 {} ".format(error)
    
    def on_ws_close(self, ws):
        "websocket关闭"
        print "websocket关闭"
        self.on_close()
    
    def on_ws_open(self, ws):
        """websocket打开"""
        print('已连接到aria2...')
    
    def close(self):
        self.ws.close()
