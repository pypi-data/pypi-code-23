# coding=utf-8
from __future__ import unicode_literals

import zmq
from om.message import Topic, Message


class HealthzStatus:
    OK = "ok"
    ERROR = "error"


class Healthz(object):
    def __init__(self, config=None, socket=None):
        self.pub_socket = None
        self.version = "unknown"
        self.name = "unknown"

        if socket:
            self.subscribe(socket)

        if config:
            self.connect(config.BROKER_HOST, config.BROKER_SUB_PORT)
            self.version = config.VERSION
            self.name = config.NAME

    def connect(self, broker_host, broker_sub_port):
        context = zmq.Context()
        self.pub_socket = context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://{}:{}".format(broker_host, broker_sub_port))

    def status_dict(self, status, _message=None, **meta):
        result = {
            "status": status,
            "meta": meta,
            "version": self.version,
            "name": self.name
        }
        if _message:
            result["message"] = _message
        return result

    def ok(self, **meta):
        return self.status_dict(HealthzStatus.OK, **meta)

    def error(self, message, **meta):
        return self.status_dict(HealthzStatus.ERROR, message, **meta)

    def subscribe(self, socket):
        socket.subscribe(Topic.HEALTH)

    def process(self, topic, message):
        if topic != Topic.HEALTH:
            return False
        if "ping" not in message:
            return True
        message = Message(
            name=self.name,
            type="healthz",
            pong=self.check()
        )
        message.to_socket(self.pub_socket, Topic.HEALTH)
        return True

    def check(self):
        return self.status_dict(HealthzStatus.OK)


class RedisHealthz(Healthz):
    def __init__(self, redis, config=None, socket=None):
        super(RedisHealthz, self).__init__(config=config, socket=socket)
        self.redis = redis

    def check(self):
        try:
            ok = self.redis.ping()
        except Exception as e:
            return self.error("redis server not reachable: {}".format(str(e)))

        return self.ok() if ok else self.error("redis server not reachable")
