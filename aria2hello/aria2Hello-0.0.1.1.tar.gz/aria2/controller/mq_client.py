# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import logging
import json
import threading
from aria2_api import Aria2Api


class MQClient(object):
    client = None
    aria2_api = None
    
    def __init__(self, device_id):
        self.device_id = device_id
    
    def get_aria2_api(self):
        return self.aria2_api
  
    def set_aria2_api(self, value):
        self.aria2_api = value
    
    def connect(self):
        """连接"""
        self.client = mqtt.Client()
        self.client.on_connect = self.on_mq_connect
        self.client.on_message = self.on_mq_message
        self.client.on_subscribe = self.on_mq_subscribe
        self.client.username_pw_set('aria2', 'aria2')
        
        def run(client, e):
           
            client.connect("10.211.55.5", 1883, 60)
            client.loop_forever()

        t1 = threading.Thread(target=run, name='mq', args=(self.client, ' '))
        t1.start()

        # def run1(client, ws, message):
        #     print "收到通知：%s" % message
        #     client.publish('0', message)
        #
        # t1 = threading.Thread(target=run1, name='Receiver', args=(self.client, ws, message))
        # t1.start()
    
    def close(self):
        """关闭连接"""
        self.client.disconnect()
    
    def on_mq_subscribe(self, client, userdata, mid, granted_qos):
        print '订阅成功 %d' % mid
    
    def on_mq_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print "已连接到远程服务器..."
        else:
            print "远程服务器连接失败，稍候重试，错误码 %d" % rc
        
        client.subscribe("aria2_read/%s" % self.device_id)
    
    def on_mq_message(self, client, userdata, msg):
        """收到服务器消息"""
        print(msg.topic + " " + str(msg.payload))
        msg_obj = json.loads(str(msg.payload))
        msg_id = msg_obj['msgId']
        method = msg_obj['method']
        args = msg_obj['args']
        self.aria2_api.invoke(msg_id=msg_id, method=method, args=args, callback=self.publish)
       
    def publish(self, msg_id, message):
        """发布消息"""
        msgWapper = json.dumps({'did': self.device_id, 'msgId': msg_id, 'message': message})
        self.client.publish('aria2_write', msgWapper)
