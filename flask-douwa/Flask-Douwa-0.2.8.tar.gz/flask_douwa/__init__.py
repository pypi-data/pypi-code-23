import logging
import sys
from flask_douwa import routes
from flask_douwa.rpc.generator_id import GeneratorRpc
from flask_douwa.rpc.demo import ProxyGetRpc
from flask_douwa.cache import RedisCache
import _thread as thread
from flask_douwa import kafka_broker

redis = RedisCache()
logger = logging.getLogger(__name__)


class Douwa(object):
    client_access = list()

    def __init__(self, app=None):
        self.getid = None
        self.kafka_callback = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        host = app.config.get("GENERATORID_IP", None)
        r_host = app.config.get("REDIS_HOST", None)
        r_port = app.config.get("REDIS_PORT", None)
        r_db = app.config.get("REDIS_DB", None)
        r_pwd = app.config.get("REDIS_PWD", None)

        if not host:
            logger.error("GENERATORID_IP:随机id生成器服务器地址没有配置")
            sys.exit(0)
        if not r_host:
            logger.error("REDIS_HOST:没有配置REDIS HOST")
            sys.exit(0)
        if not r_port:
            logger.error("REDIS_PORT:没有配置REDIS PORT")
            sys.exit(0)
        if not r_db:
            logger.error("REDIS_DB:没有配置REDIS DATABASE NAME")
            sys.exit(0)

        # 随机生成id
        rpc_register = routes.register
        proto = rpc_register(GeneratorRpc)
        self.getid = ProxyGetRpc(host, proto[0], GeneratorRpc.name)

        # REDIS连接
        redis.connect(r_host, r_port, r_db, r_pwd)

        # access_token 设置永久1个月token时间
        Douwa.client_access = app.config.get("ACCESS_TOKEN", list())

        # kafka 设置
        self.consumer_pid = app.config.get("CONSUMER_PID")
        self.conf = dict()
        self.conf["bootstrap.servers"] = app.config.get("KAFKA_HOST")
        self.conf['retries'] = app.config.get("KAFKA_RETRIES", 5)

        # self.conf['sasl.mechanisms'] = "PLAIN"
        # self.conf['security.protocol'] = 'SASL_SSL'
        # self.conf["ssl.ca.location"] = app.config.get("SSL_PATH")
        # self.conf['sasl.username'] = app.config.get("KAFKA_USERNAME")
        # self.conf['sasl.password'] = app.config.get("KAFKA_PASSWORD")

        self.topic = app.config.get("TOPIC", None)

        if self.topic and self.conf["bootstrap.servers"]:
            if not self.kafka_callback:
                logging.error("启动kafka错误 没有监视函数")
                return
            logging.info("启动kafka consumter 服务")
            thread.start_new(kafka_broker.read_notification_from_ceilometer_over_kafka, (self.conf, self.topic, self.consumer_pid, self.kafka_callback))

    def send_message(self, message):
        kafka_broker.send_message(self.conf, self.topic, message)

    def generator_id(self):
        if self.getid:
            return self.getid.GeneratorId()
        else:
            raise Exception("没有初始化")

    def bind(self):
        def wrapper(func):
            if  self.kafka_callback:
                raise AttributeError('有存在的topic')
            self.kafka_callback = func
        return wrapper
