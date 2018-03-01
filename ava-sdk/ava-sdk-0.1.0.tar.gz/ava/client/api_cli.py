# -*- coding: utf-8 -*-

import json
from ava.env import environment
from ava.utils import utils
from ava.utils import fetcher
from ava.log.logger import logger

DEFAULT_APISERVER_HOST = "http://atnet-apiserver"


class APIClient(object):
    """AVA API Client
    """

    def __init__(self, ak=None, sk=None):
        """初始化 API Client 实例

        Args:
            ak(optional): 用户 access key
            sk(optional): 用户 secret key

        Returns:
            APIClient

        Raises:
            Exception: 当 ak / sk 获取失败时抛出
        """
        if ak != None and sk != None:
            self.ak = ak
            self.sk = sk
        else:
            self.ak = utils.fetch_config_from_userinfo("key")
            self.sk = utils.fetch_config_from_userinfo("secret")
        if self.ak == None or self.sk == None:
            raise Exception("cannot init apiserver client, no ak or sk")
        self.fetcher = fetcher.QMacAuthFetcher(self.ak, self.sk)

        self.apiserver_host = utils.fetch_config_from_workerinfo(
            "atnet_apiserver_host", default=None)
        if self.apiserver_host == None:
            self.apiserver_host = DEFAULT_APISERVER_HOST

        self.train_task_name = utils.fetch_config_from_trainingspec(
            "name", default="")
        self.eval_task_name = utils.fetch_config_from_evaluationinfo(
            "name", default="")
        if self.train_task_name == "" and self.eval_task_name == "":
            raise Exception(
                "cannot init apiserver client, no train|eval task name")

    def create_train_instance(self, train_ins_spec):
        """申请创建训练实例

        Args:
            train_ins_spec:     <TrainingInstanceSpec>

        Returns:
            (id, Exception):     训练实例 ID
        """
        api_url = self.apiserver_host + \
            "/v1/trainings/%s/instances" % (self.train_task_name)
        (res, err) = self.fetcher.fetch(
            api_url, method="POST", data=train_ins_spec)
        if err != None:
            return (0, err)
        res_data = res.json()
        train_ins_id = res_data.get("id")
        if train_ins_id != None:
            return (train_ins_id, None)
        else:
            return (0, Exception("no field id in resp body"))

    def get_train_instance(self, train_instance_id):
        """获取训练实例信息

        Args:
            train_instance_id:  训练实例ID

        Returns:
            (train_ins_info, Exception):
                训练实例信息 TrainingInstanceInfo，以及
                异常信息，None 表示正常返回
        """
        api_url = self.apiserver_host + \
            "/v1/trainings/%s/instances/%s" % (
                self.train_task_name, train_instance_id)
        train_ins_info = None
        (res, err) = self.fetcher.fetch(api_url)
        if err != None:
            return (train_ins_info, err)
        logger.info("res: %s", res.text)
        train_ins_info = res.json()
        return (train_ins_info, None)

    def update_train_instance(self, train_instance_id, train_ins_spec):
        """更新训练实例状态

        Args:
            train_instance_id:  训练实例ID
            train_ins_spec:     <TrainingInstanceSpec>

        Returns:
            Exception: 更新出现的异常信息，None代表更新完成
        """
        api_url = self.apiserver_host + \
            "/v1/trainings/%s/instances/%s" % (
                self.train_task_name, train_instance_id)
        (res, err) = self.fetcher.fetch(
            api_url, method="PUT", data=train_ins_spec)
        return err

    def create_model(self, model_spec):
        """创建模型

        Args:
            model_sepc: 参考 https://github.com/qbox/ava/blob/dev/docs/AtNet.md#%E7%BD%91%E7%BB%9C%E6%A8%A1%E5%9E%8B%E5%AE%9A%E4%B9%89
        """
        api_url = self.apiserver_host + "/v1/models"
        (res, err) = self.fetcher.fetch(
            api_url, method="POST", data=model_spec)
        return err

    def get_model(self, name):
        """查询模型

        Args:
            name: 模型名称

        Returns:
            (model_info, err):
                model_info: 模型信息，ref: https://github.com/qbox/ava/blob/dev/docs/AtNet.md#%E7%BD%91%E7%BB%9C%E6%A8%A1%E5%9E%8B%E7%9A%84%E4%BF%A1%E6%81%AF
                err: 异常信息，None 表示正常返回
        """
        api_url = self.apiserver_host + \
            "v1/models/%s/%s?includeDetails=false" % (name, version)
        (res, err) = self.fetcher.fetch(api_url, method="GET")
        model_info = None
        if err != None:
            return (model_info, err)
        logger.info("res: %s", res.text)
        model_info = res.json()
        return (model_info, None)

    def update_eval_result(self, name, eval_result):
        """更新评估结果

        Args:
            name        : 评估任务名称
            eval_result : ref: https://github.com/qbox/ava/blob/dev/docs/AtNet.md#%E8%AF%84%E4%BC%B0%E4%BB%BB%E5%8A%A1%E4%BF%A1%E6%81%AF

        Returns:
            err: 异常信息，None 表示正常返回
        """
        if self.eval_task_name == "":
            return Exception("no eval task name")
        api_url = self.apiserver_host + \
            "/v1/evaluations/%s/result" % (name)
        (res, err) = self.fetcher.fetch(
            api_url, method="PUT", data=eval_result)
        return err
