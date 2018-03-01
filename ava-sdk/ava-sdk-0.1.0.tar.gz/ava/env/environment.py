# -*- coding: utf-8 -*-

import os
from functools import wraps


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance


@singleton
class Environment(object):
    """返回运行环境内的各类数据，例如：
          sampleset/model/training/... 文件路径/内容
    """

    def __init__(self, workdir=None):
        self.job_id = get_job_id()
        if workdir == None:
            self.workdir = "/workspace"
        else:
            self.workdir = workdir
        #   config
        self.config_base_path = self.workdir + "/config"
        #   params
        self.params_base_path = self.workdir + "/params"
        self.params_file = self.params_base_path + "/default.json"
        #   trainset
        self.trainset_base_path = self.workdir + "/data/train"
        self.trainset_spec_file = self.config_base_path + "/trainsetinfo"
        #   valset
        self.valset_base_path = self.workdir + "/data/val"
        self.valset_spec_file = self.config_base_path + "/valsetinfo"
        #   testset
        self.testset_base_path = self.workdir + "/data/test"
        self.testset_spec_file = self.config_base_path + "/testsetinfo"
        #   model
        self.model_base_path = self.workdir + "/model"
        self.model_spec_file = self.config_base_path + "/modelspec"
        #   training
        self.training_spec_file = self.workdir + "/config/trainingspec"
        #   user
        self.user_info_file = self.config_base_path + "/user"
        #   worker
        self.worker_info_file = self.config_base_path + "/worker"
        #   evaluation
        self.evaluation_info_file = self.config_base_path + "/evaluationinfo"
        #   dataset
        self.dataset_info_file = self.config_base_path + "/datasetinfo"


def get_job_id():
    job_name = os.getenv("JOB_NAME", "")
    try:
        job_id = job_name.split("-")[2]
    except IndexError:
        job_id = ""
    return job_id
