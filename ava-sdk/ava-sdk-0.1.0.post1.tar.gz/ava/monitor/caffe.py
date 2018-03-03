# -*- coding: utf-8 -*-

import re
import sys
import math
import time
from urlparse import urlparse

from ava.monitor import common
from ava.monitor.probe import probe
from ava.log.logger import logger
from ava.monitor.parser import caffe as caffe_parser
from ava.utils.error import (ProbeError,
                             TrainConfigError,
                             CaffeMonitorError)
from ava.monitor.config import TrainConfig
from ava.monitor.probe.probe import ProbeConfig
from ava.env import environment
from ava.utils import utils
from ava.utils import config


def get_epoch_end_log_callback(training_ins, batch_of_epoch=None, other_files=[]):
    """解析 log，上报 snapshot model

    Args:
        training_ins    : TraningInstance 实例
        batch_of_epoch  : 一个 epoch 中的 batch 数
        other_files     : 上传 snapshot model 时，需要一起打包的其他文件

    Returns:
        callback 函数
    """
    pattern = re.compile(
        ".*Snapshotting.*to binary proto file.*iter_(?P<batch>\d+).*solverstate")

    if batch_of_epoch == None:
        logger.warning(
            "get_epoch_end_log_callback failed, batch_of_epoch is None")
        return None

    def trigger(l):
        if l is True or pattern.match(l):
            logger.info("found snapshot output, trigger uploader")
            m = pattern.search(l)
            cur_batch_num = float(m.group("batch"))
            cur_epoch = utils.ceil_by_level(cur_batch_num / batch_of_epoch)
            err = training_ins.upload_snapshot_model(
                cur_epoch, batch_of_epoch, other_files)
            if err != None:
                logger.warning("upload snapshot model failed, err: %s", err)

    return trigger


def get_log_callback(training_ins_id=None):
    env = environment.Environment()
    job_id = env.job_id
    if training_ins_id == None:
        training_ins_id = job_id    # 非高级训练场景下，training_ins_id == job_id
    logger.info("prepare_monitor, training_ins_id: [%s]", training_ins_id)
    if job_id == "" or training_ins_id == "":
        logger.error(
            "prepare_monitor failed, job_id or training_ins_id is empty")
        return None

    try:
        train_config = TrainConfig()
        train_config.job_type = "training"
        train_config.job_id = job_id
        train_config.training_ins_id = training_ins_id
        train_config.training_sample_num = utils.get_sampleset_num()
        _, train_config.batch_size, train_config.val_batch_size = utils.get_batch_size()
        train_config.batch_num_of_epoch = utils.ceil_by_level(
            float(train_config.training_sample_num) / train_config.batch_size, 100)

        if train_config.training_sample_num <= 0:
            raise TrainConfigError(
                "train_config is invalid, training_sample_num <= 0")
        if train_config.job_id == "":
            raise TrainConfigError(
                "train_config is invalid, no job_id")
        if train_config.training_ins_id == "":
            raise TrainConfigError(
                "train_config is invalid, no training_ins_id")

        atnet_status_host = utils.fetch_config_from_workerinfo(
            "atnet_status_host")
        if atnet_status_host is None:
            raise CaffeMonitorError(
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

        monitor = CaffeMonitor(
            train_config=train_config,
            probe_config=probe_config)
    except TrainConfigError as e:
        logger.error("prepare_monitor, init train conf failed! err: %s", e)
        monitor = None
    except CaffeMonitorError as e:
        logger.error(
            "prepare_monitor, init caffe monitor failed! err: %s", e)
        monitor = None
    except Exception as e:
        logger.error("prepare_monitor, unknown err: %s", e)
        monitor = None

    if monitor != None:
        return monitor.monitor_from_log
    else:
        return None


class CaffeMonitor(object):
    """Caffe框架指标监控
    """

    def __init__(self, train_config, probe_config):
        """初始化

        Args:
                train_config: TrainConfig
                probe_config: ProbeConfig
        Raises:
                CaffeMonitorError
        """

        """
        训练和监控相关配置
        """
        self.train_config = train_config
        self.probe_config = probe_config
        try:
            self.probe = probe.Probe(probe_config)
        except ProbeError as err:
            raise CaffeMonitorError(
                "CaffeMonitor init failed, probe config is invalid")

        """
        在训练中需要保留的中间数据
        """
        # 每个指标当前处理的iteration(batch)
        self.cur_iter_map = {
            common.TRAINING_SAMPLE_NUM: -1,
            common.TRAINING_LOSS: -1,
            common.TRAINING_LR: -1,
            common.TRAINING_VAL_ACCURACY: -1,
        }
        # 当前一共处理了多少个batch
        self.cur_total_batch = 0
        # 在前epoch，处理了多少batch
        self.batch_in_epoch = 0

    def monitor_from_log(self, line):
        """通过日志上报监控指标

        Args:
                line:   行粒度日志文本
        """
        metric_list = self._parse_log(line)
        if len(metric_list) == 0:
            return
        succ = self.probe.mark(metric_list)
        if not succ:
            logger.warning("upload metrics failed, log line: %s", line)

    def _parse_log(self, line):
        """将日志行解析为监控指标

        Args:
                line:   行粒度日志文本

        Returns:
                list of ProbeMonitor
        """
        metric_list = []

        stats = caffe_parser.parse(line)
        if stats is None or stats.dt is None:
            return metric_list
        if stats.iteration is None:
            stats.iteration = -1
        if stats.iteration > self.cur_total_batch:
            self.cur_total_batch = stats.iteration

        # epoch 从0开始计算
        cur_epoch = int(self.cur_total_batch /
                        self.train_config.batch_num_of_epoch)
        self.batch_in_epoch = int(self.cur_total_batch %
                                  self.train_config.batch_num_of_epoch)

        # 样本处理数
        if self.cur_iter_map[common.TRAINING_SAMPLE_NUM] < stats.iteration:
            cur_sample = self.cur_total_batch * self.train_config.batch_size

            m = probe.ProbeMetric()
            m.time = time.mktime(stats.dt.timetuple())
            m.measurement = common.TRAINING_SAMPLE_NUM
            # batch等于iteration, 只是各处叫法不一致，下同
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, cur_epoch, self.cur_total_batch]
            m.fieldk_list = ['count']
            m.fieldv_list = [cur_sample]

            # 更新中间统计结果
            self.cur_iter_map[common.TRAINING_SAMPLE_NUM] = stats.iteration
            metric_list.append(m)

        # loss
        if self.cur_iter_map[common.TRAINING_LOSS] < stats.iteration and stats.loss != None:
            m = probe.ProbeMetric()
            m.time = time.mktime(stats.dt.timetuple())
            m.measurement = common.TRAINING_LOSS
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, cur_epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [stats.loss]

            # 更新中间统计结果
            self.cur_iter_map[common.TRAINING_LOSS] = stats.iteration
            metric_list.append(m)

        # lr
        if self.cur_iter_map[common.TRAINING_LR] < stats.iteration and stats.lr != None:
            m = probe.ProbeMetric()
            m.time = time.mktime(stats.dt.timetuple())
            m.measurement = common.TRAINING_LR
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, cur_epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [stats.lr]

            # 更新中间统计结果
            self.cur_iter_map[common.TRAINING_LR] = stats.iteration
            metric_list.append(m)

        # accuracy, 当前解析没有 stats.iteration，使用 TRAINING_SAMPLE_NUM 的iteration
        if stats.accuracy != None:
            iteration = stats.iteration if stats.iteration != None and stats.iteration > 0 else self.cur_iter_map.get(
                common.TRAINING_SAMPLE_NUM, -1)
            if iteration < 0:
                return metric_list
            m = probe.ProbeMetric()
            m.time = time.mktime(stats.dt.timetuple())
            m.measurement = common.TRAINING_VAL_ACCURACY
            m.tagk_list = ['job_type', 'id', 'epoch', 'batch']
            m.tagv_list = [self.train_config.job_type,
                           self.train_config.training_ins_id, cur_epoch, self.cur_total_batch]
            m.fieldk_list = ['value']
            m.fieldv_list = [stats.accuracy]

            # 更新中间统计结果
            self.cur_iter_map[common.TRAINING_VAL_ACCURACY] = stats.iteration
            metric_list.append(m)

        # TODO
        # 其它指标

        # 一些 meta 信息，使用 tagkv 来存储，value 值无所谓
        if len(metric_list) > 0:
            m = probe.ProbeMetric()
            m.time = time.mktime(stats.dt.timetuple())
            m.measurement = common.TRAINING_META_INFO
            m.tagk_list = ['job_type', 'id',
                           'epoch', 'batch', 'batch_in_epoch']
            m.tagv_list = [self.train_config.job_type, self.train_config.training_ins_id,
                           cur_epoch, self.cur_total_batch, self.batch_in_epoch]
            m.fieldk_list = ['value']
            m.fieldv_list = [1]
            metric_list.append(m)

        return metric_list
