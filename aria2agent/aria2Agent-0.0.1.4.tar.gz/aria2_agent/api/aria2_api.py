# -*- coding: utf-8 -*-
import urllib2, json


class Aria2Api(object):
    """调用Aria2接口"""
    
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
    
    def invoke(self, msg_id, method, args, callback):
        """调用aria2方法"""
        params = []
        if self.password:
            params.append('token:{}'.format(self.password))
        if args is not None and len(args) > 0:
            for arg in args:
                params.append(arg)
        jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'wechat_controller', 'method': method,
                              'params': params})
        try:
            c = urllib2.urlopen('http://{}:{}/jsonrpc'.format(self.ip, self.port), jsonreq)
            resp = c.read()
            # 发回消息
            callback(msg_id=msg_id, message=resp)
        except:
            """调用接口异常，可能是状态错误，或io异常"""
            print "接口异常"
            resp = {"error": 1}
            callback(msg_id=msg_id, message=resp)
    
    def test(self):
        params = []
        if self.password:
            params.append('token:{}'.format(self.password))
        jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'wechat_controller', 'method': 'aria2.tellActive',
                              'params': params})
        c = urllib2.urlopen('http://{}:{}/jsonrpc'.format(self.ip, self.port), jsonreq)
        resp = c.read()
