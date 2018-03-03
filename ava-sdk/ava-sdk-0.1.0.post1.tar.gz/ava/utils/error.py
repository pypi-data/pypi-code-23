# -*- coding: utf-8 -*-


class ConfigError(Exception):
    """ 配置错误异常。"""
    pass


class ProbeError(Exception):
    """
        Probe初始化错误
    """

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class TrainConfigError(Exception):
    """
        训练监控配置错误
    """

    def __init__(self, train_config):
        Exception.__init__(self)
        self.train_config = train_config

    def __str__(self):
        return "invalid train config: %s" % (self.train_config)


class CaffeMonitorError(Exception):
    """
        Caffe框架监控异常
    """

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class MxnetMonitorError(Exception):
    """
        Mxnet框架监控异常
    """

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg
