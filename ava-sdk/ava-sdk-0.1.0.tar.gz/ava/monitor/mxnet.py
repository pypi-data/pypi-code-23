# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
import math
import time
import pprint
import math
import datetime
from urlparse import urlparse

import mxnet as mx

from ava.monitor import parser
from ava.monitor import config
from ava.monitor import common
from ava.monitor.config import TrainConfig
from ava.monitor.probe import probe
from ava.monitor.probe.probe import ProbeConfig
from ava.utils.fileloc import file_location
from ava.log.logger import logger
from ava.utils.config import (fetch_config,
                              get_batch_size,
                              get_cores,
                              get_crop_size)
from ava.utils.utils import ceil_by_level
from ava.utils.error import (ProbeError,
                             TrainConfigError,
                             MxnetMonitorError)
from ava.env import environment


def batch_end_callback_builder(actual_batch_size, frequent, training_ins_id=None):
    """batch 粒度的 callback 函数列表

        Args:
            actual_batch_size:
                batch_size * gpu cores, when gpu mode
                batch_size, when cpu mode
            frequent:       触发 callback 的 batch 间隔
            training_ins_id:    训练实例ID

        Returns:
            callback 函数的列表

    """
    monitor = MxnetMonitor(training_ins_id=training_ins_id,
                           batch_size=actual_batch_size)
    monitor_func = monitor.monitor_callback

    cbs = []
    cbs.append(
        monitor_wrapper(
            mx.callback.Speedometer(actual_batch_size, frequent), monitor_func,
            frequent))

    def display_lr(param):
        if param.nbatch % frequent == 0:
            # exception is raised when detection, TODO
            # AttributeError: 'MutableModule' object has no attribute
            # '_optimizer'
            try:
                lr = param.locals["self"]._optimizer._get_lr(0)
            except Exception as e:
                lr = float("nan")
            logger.info("Epoch[%d] Batch [%d] learning-rate: %r", param.epoch,
                        param.nbatch, lr)

    cbs.append(monitor_wrapper(display_lr, monitor_func, frequent))
    return cbs


def epoch_end_callback_builder(training_ins, batch_of_epoch, other_files=[], epoch_interval=1):
    """epoch 粒度的 callback 函数

    Args:
        training_ins    : TraningInstance 实例
        batch_of_epoch  : 一个 epoch 中的 batch 数
        other_files     : 上传 snapshot model 时，需要一起打包的其他文件
        epoch_interval  : 经过多少个 epoch 运行一次 callback

    Returns:
        callback 函数
    """
    epoch_interval = int(max(1, epoch_interval))

    def callback(iter_no, sym, arg, aux):
        if (iter_no + 1) % epoch_interval == 0:
            err = training_ins.upload_snapshot_model(
                iter_no + 1, batch_of_epoch, other_files)
            if err != None:
                logger.warning("upload snapshot model failed, err: %s", err)

    return callback


class MxnetMonitor(object):
    """Mxnet框架指标监控
    """

    def __init__(self, train_config=None, probe_config=None, training_ins_id=None, batch_size=None):
        """初始化

        Args:
                train_config:       TrainConfig
                probe_config:       ProbeConfig
                training_ins_id:    训练ID
                batch_size:
        Raises:
                MxnetMonitorError
        """

        """
        训练和监控相关配置
        """
        self.train_config = train_config or get_default_train_config(training_ins_id=training_ins_id,
                                                                     batch_size=batch_size)
        self.probe_config = probe_config or get_default_probe_config(
            training_ins_id=training_ins_id)

        try:
            self.probe = probe.Probe(self.probe_config)
        except ProbeError as err:
            raise MxnetMonitorError(
                "MxnetMonitor init failed, probe config is invalid")
        # 已经处理的总样本数
        self.prev_total_sample_num = 0
        self.cur_total_batch = 0

    def monitor_callback(self, param):
        """通过mxnet框架的callback机制，获取监控指标

        Args:
                param:   mxnet框架的callback参数
        """
        metric_list = self._parse_metrics(param)
        if len(metric_list) == 0:
            return
        succ = self.probe.mark(metric_list)
        if not succ:
            logger.warning("upload metrics failed, log line: %s", line)

    def _parse_metrics(self, param):
        metric_list = []
        metric_value_map = dict()
        now = datetime.datetime.now()
        cur_time = time.mktime(now.timetuple())

        for name, value in param.eval_metric.get_name_value():
            metric_value_map[name] = value

        # param.nbatch 指的是当前epoch中的batch数量，每到一个新epoch，param.nbatch就会重新计算
        cur_total_batch = int(param.nbatch + param.epoch *
                              self.train_config.batch_num_of_epoch)
        if cur_total_batch > self.cur_total_batch:
            self.cur_total_batch = cur_total_batch

        # 样本处理数
        cur_total_sample_num = self.train_config.training_sample_num * \
            param.epoch + self.train_config.batch_size * param.nbatch
        if cur_total_sample_num > self.prev_total_sample_num:
            m = probe.ProbeMetric()
            m.time = cur_time
            m.measurement = common.TRAINING_SAMPLE_NUM
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, param.epoch, self.cur_total_batch]
            m.fieldk_list = ['count']
            m.fieldv_list = [cur_total_sample_num]
            metric_list.append(m)
            self.prev_total_sample_num = cur_total_sample_num

        # loss
        if 'cross-entropy' in metric_value_map and math.isnan(metric_value_map['cross-entropy']) == False:
            m = probe.ProbeMetric()
            m.time = cur_time
            m.measurement = common.TRAINING_LOSS
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, param.epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [metric_value_map['cross-entropy']]
            metric_list.append(m)

        # lr
        # exception is raised when detection, TODO
        # AttributeError: 'MutableModule' object has no attribute '_optimizer'
        try:
            lr = param.locals["self"]._optimizer._get_lr(0)
        except Exception as e:
            lr = float("nan")

        if math.isnan(lr) == False:
            m = probe.ProbeMetric()
            m.time = cur_time
            m.measurement = common.TRAINING_LR
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, param.epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [lr]
            metric_list.append(m)

        # accuracy
        if 'accuracy' in metric_value_map and math.isnan(metric_value_map['accuracy']) == False:
            m = probe.ProbeMetric()
            m.time = cur_time
            m.measurement = common.TRAINING_VAL_ACCURACY
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, param.epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [metric_value_map['accuracy']]
            metric_list.append(m)

        # 其它指标 TODO

        # 一些 meta 信息，使用 tagkv 来存储，value 值无所谓
        if len(metric_list) > 0:
            m = probe.ProbeMetric()
            m.time = cur_time
            m.measurement = common.TRAINING_META_INFO
            m.tagk_list = ['job_type', 'id',
                           'epoch', 'batch', 'batch_in_epoch']
            m.tagv_list = [self.train_config.job_type, self.train_config.training_ins_id,
                           param.epoch, self.cur_total_batch, param.nbatch]
            m.fieldk_list = ['value']
            m.fieldv_list = [1]
            metric_list.append(m)

        return metric_list


def get_default_train_config(training_ins_id=None, batch_size=None):
    env = environment.Environment()
    train_config = TrainConfig()
    train_config.job_type = "training"
    train_config.job_id = env.job_id
    if training_ins_id == None:
        # default config, training_ins_id == job_id
        training_ins_id = train_config.job_id
    train_config.training_ins_id = training_ins_id
    train_config.training_sample_num = fetch_config(
        env.workdir, "trainsetinfo", "stats.numOfSamples")
    if batch_size == None:
        _, train_config.batch_size, _ = get_batch_size(env.workdir)
    else:
        train_config.batch_size = batch_size
    # mxnet 不需要像 caffe 对 batch_num_of_epoch 进行按 100 进行向上取整
    train_config.batch_num_of_epoch = ceil_by_level(
        float(train_config.training_sample_num) / train_config.batch_size)
    if train_config.training_sample_num <= 0:
        raise TrainConfigError(
            "train_config is invalid, training_sample_num <= 0")
    if train_config.job_id == "":
        raise TrainConfigError("train_config is invalid, no job_id")
    if train_config.training_ins_id == "":
        raise TrainConfigError("train_config is invalid, no training_ins_id")

    return train_config


def get_default_probe_config(training_ins_id=None):
    env = environment.Environment()
    if training_ins_id == None:
        training_ins_id = env.job_id  # default config, use job_id as training_ins_id
    atnet_status_host = fetch_config(env.workdir, "worker",
                                     "atnet_status_host")
    if atnet_status_host is None:
        raise MxnetMonitorError(
            "no conf param atnet_status_host")
    probe_config = ProbeConfig()
    o = urlparse(atnet_status_host)
    if o.scheme != "":
        probe_config.server_scheme = o.scheme
    else:
        probe_config.server_scheme = "http"
    probe_config.server_host = o.netloc
    if o.path != "":
        probe_config.server_path = o.path
    else:
        probe_config.server_path = "v1/report/trainings/%s/metric" % (
            training_ins_id)

    return probe_config


def monitor_wrapper(callback, monitor_func, frequent):
    def wrapper(param):
        if param.nbatch % frequent == 0:
            monitor_func(param)
        callback(param)

    return wrapper


def full_mxnet_metrics():
    """mxnet 常用 metric 列表 
    """
    mtr = mx.metric.CompositeEvalMetric()
    child_metrics = (
        mx.metric.Accuracy(),
        mx.metric.CrossEntropy(),
        # mx.metric.F1(),
        mx.metric.MAE(),
        mx.metric.MSE(),
        mx.metric.RMSE(),
        mx.metric.TopKAccuracy(top_k=5))
    for child_metric in child_metrics:
        mtr.add(child_metric)
    return mtr
