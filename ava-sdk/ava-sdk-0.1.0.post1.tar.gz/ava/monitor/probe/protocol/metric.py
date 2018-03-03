# -*- coding: utf-8 -*-


class ProbeMetric(object):
    """探针上报数据信息
    格式参考：
            https://github.com/qbox/base/tree/develop/qiniu/src/qiniu.com/probe
    """

    def __init__(self):
        self.measurement = ''
        self.time = None  # time.time()
        self.tagk_list = []
        self.tagv_list = []
        self.fieldk_list = []
        self.fieldv_list = []

    def __str__(self):
        return 'm:%s,t:%s,tagk:%s,tagv:%s,fieldk:%s,fieldv:%s' % (
            self.measurement,
            self.time,
            self.tagk_list,
            self.tagv_list,
            self.fieldk_list,
            self.fieldv_list)
