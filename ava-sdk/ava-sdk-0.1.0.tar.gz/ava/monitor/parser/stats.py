#!/usr/bin/env python
# -*- coding: utf-8 -*-


class IntervalTrainStats(object):
    """训练过程中根据每一行解析的统计信息
    """

    def __init__(self):
        self.iteration = None  # iteration == nbatch
        self.epoch = None
        self.accuracy = None
        self.lr = None
        self.loss = None
        self.dt = None  # datetime.datetime类型

    def __str__(self):
        return "iter:%s,epoch:%s,accu:%s,lr:%s,loss:%s,dt:%s" % (
            self.iteration,
            self.epoch,
            self.accuracy,
            self.lr,
            self.loss,
            self.dt,
        )
