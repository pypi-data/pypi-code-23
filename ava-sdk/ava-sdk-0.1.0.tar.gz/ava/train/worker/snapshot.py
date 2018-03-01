#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import traceback
import sys
import threading
import Queue

from ava.client import api_cli
from ava.log.logger import logger
from ava.utils import uploader
from ava.utils import compress
from ava.utils import fileloc


class SnapshotModelUploadMsg(object):
    """传递给 SnapshotModelUploader 的消息"""

    def __init__(self):
        self.model_file_list = []       # snapshot model 包含的文件列表
        self.extra_file_list = []       # 其他地方（例如 sampleset ）的文件
        self.model_tar_base_dir = ""    # tar 包生成的目录
        self.model_tar_fname = ""       # tar 包名称
        self.kodo_key = ""              # 上传的 kodo key
        self.model_spec = {}            # 添加至 ava 后台的 model spec

    def __str__(self):
        s = ""
        s += "model_file_list: %s\n" % (self.model_file_list)
        s += "extra_file_list: %s\n" % (self.extra_file_list)
        s += "model_tar_base_dir: %s\n" % (self.model_tar_base_dir)
        s += "model_tar_fname: %s\n" % (self.model_tar_fname)
        s += "kodo_key: %s\n" % (self.kodo_key)
        s += "model_spec %s\n" % (json.dumps(self.model_spec, indent=2))
        return s


class SnapshotModelUploader(threading.Thread):
    """从 Queue 中获取 snapshot model 信息，
    然后打包上传至 Kodo 存储
    """

    def __init__(self, queue, ak, sk, bucket):
        """初始化

        Args：
            queue   : snapshot model 消息队列
            ak      : access key
            sk      : secret key
            bucket  : user bucket
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.ak = ak
        self.sk = sk
        self.bucket = bucket
        # kodo uploader
        self.uploader = uploader.Uploader(
            self.ak, self.sk, bucket=self.bucket)
        # api client
        self.api_cli = api_cli.APIClient(ak=self.ak, sk=self.sk)

    def run(self):
        logger.debug("snapshot model uploader started")
        while True:
            msg = self.queue.get()
            if msg == None:
                logger.debug("receive msg None, exit")
                return
            logger.debug("msg: %s", msg)
            fileloc.mkdir_p(msg.model_tar_base_dir)
            model_tar_file = os.path.join(
                msg.model_tar_base_dir, msg.model_tar_fname)
            try:
                # tar files
                logger.debug("compress file: %s, input_files: %s",
                             model_tar_file, msg.model_file_list)
                err = _do_compress_files(
                    msg.model_file_list, model_tar_file)
                if err != None:
                    logger.warning("compress files failed, err: %s", err)
                    raise err
                # upload onto kodo
                logger.debug(
                    "uploading onto kodo, model_tar_file: %s, kodo_key: %s", model_tar_file, msg.kodo_key)
                self.uploader.upload_file(model_tar_file, msg.kodo_key)
                # create model spec
                logger.debug("create model, model spec: %s",
                             json.dumps(msg.model_spec, indent=2))
                err = self.api_cli.create_model(msg.model_spec)
                if err != None:
                    logger.warning("create model_spec failed, err: %s", err)
                    raise err
            except Exception as err:
                logger.warning(
                    "process snapshot model failed, err: %s", err)
                traceback.print_exc(file=sys.stderr)
                continue
            finally:
                logger.debug("delete model tar file: %s", model_tar_file)
                fileloc.rm_path(model_tar_file)
                # 只删除 model_file_list 中的文件，保留 extra_file_list
                for fname in msg.model_file_list:
                    logger.debug("delete model file: %s", fname)
                    fileloc.rm_path(fname)


def _do_compress_files(file_list, output_file):
    _wait_files_writing(file_list)
    ret = compress.tar_files(file_list, output_file)
    if ret != None:
        logger.warning("compress tar file failed, err: %s", ret)
        return ret


def _wait_files_writing(file_list):
    file_size_dict = {}
    while True:
        wait = False
        for file_path in file_list:
            # what if file_path is dir? FIXME
            try:
                size = os.path.getsize(file_path)
                if file_path not in file_size_dict or file_size_dict[file_path] != size:
                    wait = True
                    file_size_dict[file_path] = size
            except Exception as e:
                logger.warning("get file size failed, err: %s", e)
                continue
        if wait:
            logger.debug("wait files for writing, wait a while")
            time.sleep(1)
        else:
            return
