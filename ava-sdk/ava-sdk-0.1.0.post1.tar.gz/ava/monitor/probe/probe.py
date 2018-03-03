# -*- coding: utf-8 -*-

import time
import sys
from urlparse import urlparse
import threading
import Queue
import requests
from protocol.encode import encode
from protocol.metric import ProbeMetric
from ava.log.logger import logger
from ava.utils.error import ProbeError


class ProbeConfig(object):
    """探针配置信息"""

    def __init__(self,
                 server_scheme=None,
                 server_host=None,  # domain/ip and port
                 server_path=None,
                 connect_timeout_sec=None,
                 read_timeout_sec=None):
        self.server_scheme = server_scheme or 'http'
        self.server_host = server_host or 'localhost:9105'
        self.server_path = server_path or ''  # v1/report/<job_type>/<job_id>/metric
        self.connect_timeout_sec = connect_timeout_sec or 0.2  # 200 ms
        self.read_timeout_sec = read_timeout_sec or 0.5  # 500 ms


class UploadWorker(threading.Thread):
    """从Queue中读取metric_list，负责上报指标的worker"""

    def __init__(self, probe_config, metric_queue):
        """初始化UploadWorker

        Args:
            probe_config: ProbeConfig
            metric_queue: queue of metric list
        Raise:
            ProbeError: 配置错误
        """
        threading.Thread.__init__(self)
        self.probe_config = probe_config
        self.metric_queue = metric_queue
        self.probe_url = '%s://%s/%s' % (self.probe_config.server_scheme,
                                         self.probe_config.server_host, self.probe_config.server_path)
        o = urlparse(self.probe_url)
        if o.scheme == '' or o.netloc == '' or o.path == '':
            logger.error('invalid probe config: %s, %s, %s, %s', config, config.server_scheme,
                         config.server_host, config.server_path)
            raise ProbeError
        self._max_mark_metric_num = 20      # 一次最多上报20份probe metric
        self._max_metric_value_num = 10     # 一份probe metric中最大value条数
        self._upload_retry_num = 3          # 上报重试次数
        self._upload_retry_sleep = 0.2      # 上报重试sleep时间，200ms

    def run(self):
        logger.debug('upload worker started')
        while True:
            metric_list = self.metric_queue.get()
            if len(metric_list) == 0:
                continue

            succ = False
            for i in range(self._upload_retry_num):
                if i > 0:
                    time.sleep(self._upload_retry_sleep)
                succ = self.do_upload(metric_list)
                if succ:
                    break
                else:
                    logger.warning(
                        'upload metric_list failed for %d time(s)', i + 1)

            if succ:
                logger.info(
                    'upload metric_list succ, metric_list len: %d', len(metric_list))
            else:
                logger.warning(
                    'upload metric_list failed after %d time(s)', self._upload_retry_num)

    def do_upload(self, metric_list):
        if len(metric_list) > self._max_mark_metric_num:
            metric_list = metric_list[:self._max_mark_metric_num]
        encoded_metric_list = []
        for metric in metric_list:
            if len(metric.fieldk_list) > self._max_metric_value_num:
                metric.fieldk_list = metric.fieldk_list[
                    :self._max_metric_value_num]
            if len(metric.fieldv_list) > self._max_metric_value_num:
                metric.fieldv_list = metric.fieldv_list[
                    :self._max_metric_value_num]
            encoded_metric_list.append(encode(metric))
        post_content = '\n'.join(encoded_metric_list)

        try:
            r = requests.post(self.probe_url, data=post_content, timeout=(
                self.probe_config.connect_timeout_sec, self.probe_config.read_timeout_sec))
        except Exception as err:
            logger.error('post metric_list failed, err: %s', err)
            return False

        if r.status_code != requests.codes.ok:
            logger.warning('status[%d] code is not ok', r.status_code)
            return False

        resp_json = r.json()
        if resp_json.get('code') != 0:
            logger.warning('resp code is not 0, resp: %s', resp_json)
            return False

        return True


class Probe(object):
    """数据集构建/训练/评估过程中将半结构化的监测数据"""

    def __init__(self, config):
        """初始化Probe

        Args:
                config: ProbeConfig 配置
        Raise:
                ProbeError: 配置错误
        """
        self.config = config
        self.metric_queue = Queue.Queue(1024)  # buffered queue
        self.upload_worker = UploadWorker(self.config, self.metric_queue)
        self.upload_worker.setDaemon(True)
        self.upload_worker.start()

    def mark(self, metric_list):
        """上报监控数据

        Args:
                metric_list: list of ProbeMetric

        Returns:
                bool value, succeed to upload metrics or not
        """
        try:
            self.metric_queue.put_nowait(metric_list)
        except Queue.Full as err:
            logger.error('mark metric_list failed, err: %s', err)
            return False
        except Exception as err:
            logger.error('mark metric_list failed, unknwon err: %s', err)
            return False

        return True
