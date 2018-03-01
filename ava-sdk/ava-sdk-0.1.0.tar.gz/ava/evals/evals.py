#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import tarfile
import traceback

from ava.env import environment
from ava.utils import utils
from ava.utils import fetcher
from ava.utils import uploader
from ava.log.logger import logger
from ava.log.logger import initialize_logger
from ava.client import api_cli
from ava.utils.fileloc import (mkdir_p, rm_path)
from ava.evals import metrics as eval_metrics


class EvalInstance(object):
    """评估实例
    负责处理 ava 平台中运行评估的业务
    """

    def __init__(self, label_name, problem_type):
        self.env = environment.Environment()
        self.rundir = os.path.join(self.env.workdir, "run")
        self.log_base_path = os.path.join(self.rundir, "logs")
        self.default_input_base_path = os.path.join(self.rundir, "prepared")
        self.dataset_list_filepath = os.path.join(
            self.default_input_base_path, "dataset.json.list")
        self.default_output_base_path = os.path.join(self.rundir, "output")
        self.evals_filepath = os.path.join(
            self.default_output_base_path, "evals.json.list")
        mkdir_p(self.rundir)
        mkdir_p(self.log_base_path)
        mkdir_p(self.default_input_base_path)
        mkdir_p(self.default_output_base_path)
        mkdir_p(self.env.model_base_path)

        # eval name
        self.eval_task_name = utils.fetch_config_from_evaluationinfo(
            "name", default="")
        # user info
        self.user_id = utils.fetch_config_from_userinfo("uid")
        self.user_ak = utils.fetch_config_from_userinfo("key")
        self.user_sk = utils.fetch_config_from_userinfo("secret")
        self.user_bucket = utils.fetch_config_from_userinfo("bucket")
        # api client
        self.api_cli = api_cli.APIClient(ak=self.user_ak, sk=self.user_sk)
        # kodo uploader
        self.uploader = uploader.Uploader(
            self.user_ak, self.user_sk, bucket=self.user_bucket)

        initialize_logger(self.log_base_path, debug=True)
        self.label_name = label_name
        self.problem_type = problem_type
        self.label_classes = []
        self.acc_topn = [1]
        # eval result
        self.eval_result = {
            "scoreFile": self._generate_eval_result_file_url(),
            "metric": {},
        }

    def get_model_base_path(self):
        return self.env.model_base_path

    def prepare_data(self):
        err = self._prepare_model()
        if err != None:
            logger.warning("prepare model file failed, err: %s", err)
            return err
        err = self._get_dataset_list()
        if err != None:
            logger.warning("get dataset list failed, err: %s", err)
            return err

    def set_label_classes(self, classes):
        logger.debug("set classes: %s", classes)
        self.label_classes = classes

    def set_acc_topn(self, topn):
        self.acc_topn = topn

    def run(self, eval_func, limit=0):
        """运行评估

        Args:
            eval_func: 评估函数
                参数: local_file_path 图片本地路径
                返回值:  用户自定义 labels （ref: https://github.com/qbox/ava/blob/dev/docs/AtFlow.md）
                        err (Exception)
            limit: 评估的最大数量，0表示没有要求，用于测试
        """
        # 目前只支持串行的 eval，TODO
        tmp_image_file_path = os.path.join(
            self.default_input_base_path, "input_image")
        rm_path(self.evals_filepath)
        logger.debug("iterating dataset list: %s", self.dataset_list_filepath)
        i = 0
        dataset_count = 0
        with open(self.dataset_list_filepath, "r") as dataset_file:
            for line in dataset_file:
                dataset_count += 1

        with open(self.dataset_list_filepath, "r") as dataset_file, open(self.evals_filepath, "w") as eval_file:
            for line in dataset_file:
                if limit != 0 and i >= limit:
                    break
                i += 1

                dataset_info = json.loads(line)
                logger.debug("(%d/%d) processing dataset: %s",
                             i, dataset_count, dataset_info)
                err = self._download_dataset_image(
                    dataset_info, tmp_image_file_path)
                if err != None:
                    logger.warning("download image failed, err: %s", err)
                    continue
                eval_labels, err = eval_func(tmp_image_file_path)
                if err != None:
                    logger.warning("eval_func failed, err: %s", err)
                logger.debug("eval_labels: %s", eval_labels)
                eval_json = self._generate_eval_json(dataset_info, eval_labels)
                logger.debug("eval_json: %s", eval_json)
                eval_file.write(json.dumps(eval_json) + "\n")
                rm_path(tmp_image_file_path)

        # upload eval result file
        logger.debug("uploading eval result file")
        err = self._upload_eval_result_file()
        if err != None:
            logger.warning("upload eval result failed, err: %s", err)
            return err

        # eval metrics
        logger.debug("calcuating eval metrics")
        self._calculate_and_eval_metrics()
        # save eval result
        logger.debug("saving eval result")
        err = self._update_eval_result()
        if err != None:
            logger.warning("update eval result failed, err: %s", err)
            return err

    def _generate_eval_json(self, origin_json, eval_labels):
        eval_json = origin_json
        # 在原有的 label 后追加 eval 结果
        labels = eval_json.get("label", [
                               {
                                   "name": self.label_name,
                                   "type": self.problem_type,
                                   "version": 1,
                                   "data": []
                               }])
        for label in labels:
            if label["name"] == self.label_name and label["type"] == self.problem_type:
                label["data"].extend(eval_labels)

        eval_json["label"] = labels
        return eval_json

    def _prepare_model(self):
        """下载 && 解压 模型文件
        """
        model_url = utils.fetch_config_from_modelspec("file")
        try:
            # tar or tar.gz ？ TODO
            model_file_path = os.path.join(
                self.env.model_base_path, "model.tar")
            downloader = fetcher.Fetcher(
                access_key=self.user_ak, secret_key=self.user_sk)
            downloader.fetch_huge_file(
                model_url, filepath=model_file_path)
        except Exception as e:
            logger.warning("download model failed, err: %s", e)
            return e
        tar = tarfile.open(model_file_path, "r")
        tar.extractall(path=self.env.model_base_path)
        tar.close()

    def _get_dataset_list(self):
        """下载 dataset json list 至本地

        Returns:
            err(Exception)
        """
        with open(self.env.dataset_info_file, "r") as f:
            dataset_info = json.load(f)
        dataset_list_url = dataset_info.get("indexFile")
        if dataset_list_url == None:
            return Exception("can nont get indexFile")
        logger.debug("dataset list url: %s", dataset_list_url)
        try:
            downloader = fetcher.Fetcher(
                access_key=self.user_ak, secret_key=self.user_sk)
            downloader.fetch_huge_file(
                dataset_list_url, filepath=self.dataset_list_filepath)
        except Exception as e:
            logger.warning("download dataset failed, err: %s", e)
            return e

        return None

    def _download_dataset_image(self, dataset_json, filepath):
        downloader = fetcher.Fetcher(
            access_key=self.user_ak, secret_key=self.user_sk, req_timeout=2)
        file_url = dataset_json["url"]
        logger.debug("download file url: %s => %s", file_url, filepath)
        try:
            downloader.fetch_huge_file(file_url, filepath=filepath)
        except Exception as e:
            return e
        return None

    def _upload_eval_result_file(self):
        try:
            kodo_key = self._generate_eval_result_file_kodo_key()
            logger.debug("uploading eval result file, file: %s, key: %s",
                         self.evals_filepath, kodo_key)
            self.uploader.upload_file(self.evals_filepath, kodo_key)
        except Exception as e:
            logger.warning("upload eval file failed, err: %s", e)
            logger.warning("err: %s", traceback.format_exc())
            return e
        return None

    def _generate_eval_result_file_kodo_key(self):
        return "ava/default/evaluations/%s/result.lst" % (
            self.eval_task_name)

    def _generate_eval_result_file_url(self):
        kodo_key = self._generate_eval_result_file_kodo_key()
        return "qiniu://%s@z0/%s/%s" % (self.user_id, self.user_bucket, kodo_key)

    def _calculate_and_eval_metrics(self):
        """计算评估统计值

        Returns:
            dict():
                top<n>_acc  : TopN 准确率, <n>为变量
                map         : mean average precision
        """
        metrics = eval_metrics.calculate_metric(
            self.evals_filepath, self.label_classes, self.problem_type, self.acc_topn)
        logger.debug("eval metrics: %s", metrics)
        self.eval_result["metric"] = metrics

    def _update_eval_result(self):
        return self.api_cli.update_eval_result(self.eval_task_name, self.eval_result)
