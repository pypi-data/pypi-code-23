#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import Queue

from ava.utils.fileloc import mkdir_p
from ava.utils import utils
from ava.utils import date as date_utils
from ava.utils import fetcher
from ava.utils import uploader
from ava.utils import compress
from ava.utils import fileloc
from ava.log.logger import initialize_logger
from ava.log.logger import logger
from ava.env import environment
from ava.client import api_cli
from ava.params import params
from ava.train.worker import snapshot

# 训练实例状态
TRAIN_INS_STATUS_RUNNING = "running"
TRAIN_INS_STATUS_DONE = "done"
TRAIN_INS_STATUS_FAIL = "failed"


class TrainInstance(object):
    """训练任务实例
    每一个训练实例，都会有对应的独立输出目录
    """

    def __init__(self, training_ins_id=None):
        """初始化与训练相关的路径

        训练实例的工作目录：
        /workspace
            ├── config
            |   ├── trainingspec    // 系统传入的配置文件
            │   ├── ...
            ├── params
            |   └── default.json    // 用户传递的参数json文件
            ├── data
            │   ├── test            // test data pvc
            │   ├── train           // train data pvc
            │   └── val             // val data pvc
            ├── model               // 存放模型的目录
            └── run                 // run data pvc
                ├── <training_ins_id1>
                |   ├── output      // 一次训练的 snapshot model 输出
                |   ├── tmp
                |   └── logs        // 一次训练的日志路径
                └── <training_ins_id2>

        Args:
            training_ins_id:    用户传入的训练实例ID，表明：1）用户复用之前的训练实例ID 或者 2）用户自定义的训练实例ID

        Raises:
            Exception: 训练实例创建失败错误
        """
        # user info
        self.user_id = utils.fetch_config_from_userinfo("uid")
        self.user_ak = utils.fetch_config_from_userinfo("key")
        self.user_sk = utils.fetch_config_from_userinfo("secret")
        self.user_bucket = utils.fetch_config_from_userinfo("bucket")
        # env
        self.env = environment.Environment()
        # api client
        self.api_cli = api_cli.APIClient(ak=self.user_ak, sk=self.user_sk)
        # kodo uploader
        self.uploader = uploader.Uploader(
            self.user_ak, self.user_sk, bucket=self.user_bucket)
        # training instance id
        if training_ins_id != None:
            self.training_ins_id = training_ins_id
            self.train_ins_spec, err = self.api_cli.get_train_instance(
                training_ins_id)
            if err != None:
                raise err
        else:
            self.train_ins_spec = dict()
            self.train_ins_spec["status"] = TRAIN_INS_STATUS_RUNNING
            self.train_ins_spec["params"] = params.get_all()
            self.train_ins_spec["startTime"] = date_utils.get_datetime_in_rfc3339(
            )
            self.training_ins_id, err = self.api_cli.create_train_instance(
                self.train_ins_spec)
            if err != None:
                logger.warn("get train instance id failed, err: %s", err)
                raise err
        # rundir 相关
        self.rundir = self.env.workdir + "/run/" + self.training_ins_id
        mkdir_p(self.rundir)
        # snapshot output
        self.snapshot_base_path = self.rundir + "/output"
        mkdir_p(self.snapshot_base_path)
        # logs
        self.log_base_path = self.rundir + "/logs"
        mkdir_p(self.log_base_path)
        # 初始化 ava.utils.log 中的 logger 实例
        initialize_logger(self.log_base_path, debug=True)
        # snapshot model uploader
        self.snapshot_model_queue = Queue.Queue(128)
        self.snapshot_model_uploader = snapshot.SnapshotModelUploader(
            self.snapshot_model_queue, self.user_ak, self.user_sk, self.user_bucket)
        self.snapshot_model_uploader.daemon = True
        self.snapshot_model_uploader.start()

    def get_training_ins_id(self):
        return self.training_ins_id

    def get_base_path(self):
        return self.rundir

    def get_snapshot_base_path(self):
        return self.snapshot_base_path

    def get_trainset_base_path(self):
        return self.env.trainset_base_path

    def get_valset_base_path(self):
        return self.env.valset_base_path

    def get_testset_base_path(self):
        return self.env.testset_base_path

    def get_model_base_path(self):
        return self.env.model_base_path

    def report_stop(self, err_msg=""):
        """通知服务端训练结束

        Args:
            err_msg: 错误信息，如果没空代表没有错误

        Returns:
            Exception: 调用 API Client 发生的错误
        """
        self.train_ins_spec["stopTime"] = date_utils.get_datetime_in_rfc3339()
        self.train_ins_spec["errMsg"] = err_msg
        if err_msg != "":
            self.train_ins_spec["status"] = TRAIN_INS_STATUS_FAIL
        else:
            self.train_ins_spec["status"] = TRAIN_INS_STATUS_DONE
        logger.debug("report training instance stop, spec: %s" %
                     (json.dumps(self.train_ins_spec, indent=2)))
        return self.api_cli.update_train_instance(self.training_ins_id, self.train_ins_spec)

    def done(self, err_msg=""):
        """训练结束显式调用
        """
        self.report_stop(err_msg=err_msg)
        # 其他清理工作，例如上传log，snapshot model, TODO
        # stop snapshot_model_uploader with None msg
        self.snapshot_model_queue.put(None)
        # wait for finishing
        self.snapshot_model_uploader.join()

    def get_monitor_callback(self, framework, **kwargs):
        """返回各种框架的监控回调函数

        Args:
            framework:  各个训练框架名称，目前支持：mxnet, caffe
            kwargs:     各个训练框架 callback 的初始化函数

        Returns:
            callback:   各个训练框架的回调函数, or None 表示框架不支持
        """
        callback = None
        if framework == "mxnet":
            from ava.monitor import mxnet as mxnet_monitor
            batch_size = kwargs.get("batch_size")
            if batch_size == None:
                logger.warn(
                    "mxnet monitor callback init failed, no parameter 'batch_size'")
                return None
            batch_freq = kwargs.get("batch_freq")
            if batch_freq == None:
                logger.warn(
                    "mxnet monitor callback init failed, no parameter 'batch_freq'")
                return None
            callback = mxnet_monitor.batch_end_callback_builder(
                batch_size, batch_freq,
                training_ins_id=self.training_ins_id)
        elif framework == "caffe":
            from ava.monitor import caffe as caffe_monitor
            callback = caffe_monitor.get_log_callback(
                training_ins_id=self.training_ins_id)
        else:
            logger.warn(
                "get_monitor_callback failed, unsupported framework: %s", framework)
            return None

        return callback

    def get_epoch_end_callback(self, framework, **kwargs):
        """返回各种框架的监控回调函数

        Args:
            framework:  各个训练框架名称，目前支持：mxnet
            kwargs:     各个训练框架 callback 的初始化函数

        Returns:
            callback:   各个训练框架的回调函数, or None 表示框架不支持
        """
        callback = None
        if framework == "mxnet":
            from ava.monitor import mxnet as mxnet_monitor
            other_files = kwargs.get("other_files", [])
            epoch_interval = kwargs.get("epoch_interval", 1)
            batch_of_epoch = kwargs.get("batch_of_epoch")
            if batch_of_epoch == None:
                logger.warn(
                    "no batch_of_epoch param, init epoch_end_callback failed")
                return None
            callback = mxnet_monitor.epoch_end_callback_builder(
                self, batch_of_epoch, other_files=other_files, epoch_interval=epoch_interval)
        elif framework == "caffe":
            from ava.monitor import caffe as caffe_monitor
            other_files = kwargs.get("other_files", [])
            batch_of_epoch = kwargs.get("batch_of_epoch")
            callback = caffe_monitor.get_epoch_end_log_callback(self,
                                                                batch_of_epoch=batch_of_epoch,
                                                                other_files=other_files)
        else:
            logger.warn(
                "get_monitor_callback failed, unsupported framework: %s", framework)
            return None

        return callback

    def upload_snapshot_model(self, cur_epoch, batch_of_epoch, other_files=[]):
        """上传 snapshot 模型
        采集 snapshot output 目录下的文件 以及 用户指定的文件,
        将这些文件打包上传，并且记录在 AVA 后台

        Args:
            cur_epoch       : 当前 epoch
            batch_of_epoch  : 一个 epoch 中的 batch 数
            other_files     : 其他文件文件路径列表

        Returns:
            (model_name, kodo_key, err)
                model_name:     生成的模型名称
                kodo_key:       生成的 kodo key
                err:            发生错误的 Exception，None 表示正常返回
        """
        msg = snapshot.SnapshotModelUploadMsg()
        snapshot_base_path = self.get_snapshot_base_path()
        for fname in os.listdir(snapshot_base_path):
            msg.model_file_list.append(os.path.join(snapshot_base_path, fname))
        msg.extra_file_list = other_files
        msg.model_tar_base_dir = os.path.join(self.get_base_path(), "tmp")
        msg.model_tar_fname = "snapshot-model-%d.tar.gz" % (cur_epoch)
        msg.kodo_key = self._generate_snapshot_model_kodo_key(cur_epoch)
        msg.model_spec = {
            "name": self._generate_snapshot_model_name(cur_epoch),
            "type": "snapshot",
            "file": "qiniu://%s@z0/%s/%s" % (self.user_id, self.user_bucket, msg.kodo_key),
            "params": {},       # TODO
            "trainingRef": self._generate_training_ref(cur_epoch, batch_of_epoch),
            "specVersion": "v1"
        }

        try:
            self.snapshot_model_queue.put_nowait(msg)
        except Queue.Full as err:
            logger.error("snapshot_model_queue full, err: %s", err)
            return err
        except Exception as err:
            logger.error('upload_snapshot_model failed, unknwon err: %s', err)
            return err

        logger.debug(
            "put snapshot model upload msg into queue, cur_epoch: %d", cur_epoch)
        return None

    def upload_custom_model(self, local_file_list, model_name, kodo_key):
        """上传自定义模型
        将文件列表进行打包，上传至 Kodo，在 AVA 后台进行记录

        Args:
            local_file_list:    本地文件路径列表
            model_name:         模型名称
            kodo_key:           存储在 kodo 的 file key

        Returns:
            err(Exception): 返回错误，None 表示正常
        """

        # 打包 && 上传至 kodo
        model_tar_file = os.path.join(
            self.get_base_path(), "output", "custom-model-%s.tar.gz" % (int(time.time())))
        try:
            logger.debug("create model file: %s", model_tar_file)
            compress.tar_files(local_file_list, model_tar_file)
            self.uploader.upload_file(model_tar_file, kodo_key)
        except Exception as err:
            logger.warning("err: %s", err)
            return err
        finally:
            fileloc.rm_path(model_tar_file)

        # 在 AVA 后台创建 model
        model_spec = {
            "name": model_name,
            "type": "custom",
            "file": "qiniu://%s@z0/%s/%s" % (self.user_id, self.user_bucket, kodo_key),
            "params": {},    # TODO
            "specVersion": "v1"
        }
        logger.debug("create model, model spec: %s",
                     json.dumps(model_spec, indent=2))
        ret = self.api_cli.create_model(model_spec)
        return ret

    def download_model(self, model_name, local_path):
        """下载模型至本地目录

        Args:
            model_name: 模型名称
            local_path: 下载地址

        Returns:
            err(Exception): 返回错误，None 表示正常
        """
        model_info, err = self.api_cli.get_model(model_name)
        if err != None:
            return err
        model_file_url = model_info.get("file")
        try:
            downloader = fetcher.Fetcher()
            downloader.fetch_huge_file(model_file_url, local_path)
        except Exception as e:
            logger.warning("download file failed, err: %s", e)
            return e
        return None

    def _generate_snapshot_model_kodo_key(self, cur_epoch):
        kodo_key = "ava/default/models/%s-snapshot-model:epoch_%d/snapshots/model.tar.gz" % (
            self.get_training_ins_id(), cur_epoch)
        return kodo_key

    def _generate_snapshot_model_name(self, cur_epoch):
        model_name = "%s-snapshot-model:epoch_%d" % (
            self.get_training_ins_id(), cur_epoch)
        return model_name

    def _generate_training_ref(self, cur_epoch, batch_of_epoch):
        training_ref = {}
        # training instance spec
        training_ref["instanceID"] = self.get_training_ins_id()
        for k, v in self.train_ins_spec.iteritems():
            training_ref[k] = v
        # training spec
        training_spec = utils.fetch_all_from_trainingspec()
        for k, v in training_spec.iteritems():
            training_ref[k] = v
        # metric
        training_ref["metric"] = {
            "epoch": cur_epoch,
            "batch": cur_epoch * batch_of_epoch,
            # loss 等指标  TODO
        }
        # upload time
        training_ref["modelUploadTime"] = date_utils.get_datetime_in_rfc3339()

        return training_ref
