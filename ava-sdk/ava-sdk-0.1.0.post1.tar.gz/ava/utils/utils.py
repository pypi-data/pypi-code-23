# -*- coding: utf-8 -*-

import os
import json
import math
from ava.log.logger import logger
from ava.params.params import (fetch_config_from_file, get_value)
from ava.env import environment


def fetch_config_from_samplesetinfo(key, data_type="train", is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    if data_type == "train":
        fn = env.trainset_spec_file
    elif data_type == "val":
        fn = env.valset_spec_file
    elif data_type == "test":
        fn = env.testset_spec_file
    else:
        return default

    return fetch_config_from_file(fn, key, is_required=is_required, default=default, use_cache=use_cache)


def fetch_config_from_trainingspec(key, is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    return fetch_config_from_file(env.training_spec_file, key, is_required=is_required, default=default, use_cache=use_cache)


def fetch_all_from_trainingspec():
    env = environment.Environment()
    try:
        with open(env.training_spec_file, "r") as f:
            training_spec = json.load(f)
    except Exception as err:
        logger.warning("parse traininig spec failed, err: %s", err)
        training_spec = {}
    return training_spec


def fetch_config_from_modelspec(key, is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    return fetch_config_from_file(env.model_spec_file, key, is_required=is_required, default=default, use_cache=use_cache)


def fetch_config_from_userinfo(key, is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    return fetch_config_from_file(env.user_info_file, key, is_required=is_required, default=default, use_cache=use_cache)


def fetch_config_from_workerinfo(key, is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    return fetch_config_from_file(env.worker_info_file, key, is_required=is_required, default=default, use_cache=use_cache)

def fetch_config_from_evaluationinfo(key, is_required=False, default=None, use_cache=True):
    env = environment.Environment()
    return fetch_config_from_file(env.evaluation_info_file, key, is_required=is_required, default=default, use_cache=use_cache)


def get_cores():
    """ 是否使用 GPU 及当前 worker 分配的 GPU 卡数。"""
    use_gpu = fetch_config_from_trainingspec("resource.gpus", default=0) != 0
    # TODO 分布式情况下从 totalCores 读取当前训练使用的 GPU 数量是不准的，需要其他参数接口
    # gpus 指的是卡数，对应 cores 要根据卡的型号换算
    cores = fetch_config_from_trainingspec("resource.gpus", default=1)
    return (use_gpu, cores)


def get_batch_size():
    """ 封装 batch_size 读取和计算。

    1. GPU 模式下 caffe/mxnet 真实训练batch_size 为 配置的训练batch_size * GPU 数量。
    2. GPU 模式下 caffe/mxnet 真实评估batch_size 为 配置的评估batch_size * GPU 数量。
    3. 评估 batch_size 未指定时默认为单核对应的 batch_size * GPU 数量。

    Returns:
        (batch_size, actual_batch_size, val_batch_size)
        配置的『单核』batch_size，计算的真实 batch_size，评估 batch_size 。
    """
    batch_size = get_value("solverOps.batchSize", default=8)
    val_batch_size = get_value("solverOps.valBatchSize", default=batch_size)
    use_gpu, cores = get_cores()
    logger.info("Cores GPU=%s, count=%d", use_gpu, cores)
    actual_batch_size = batch_size if not use_gpu else batch_size * cores
    if use_gpu:
        val_batch_size *= cores
    return (batch_size, actual_batch_size, val_batch_size)


def get_crop_size():
    """ 封装 crop_size 读取和计算。

    1. none/None/... ：不作剪裁。
    2. '123'： 剪裁正方形 123x123。
    3. '123x456'： 剪裁矩形 123(width)x456(height)
    4. 无法识别的 str ：不作剪裁

    Returns:
        (crop_w, crop_h) 剪裁宽度，剪裁高度；全为 None 不剪裁。

    Raises:
        ConfigError: 配置异常。
    """
    input_str = str(fetch_config_from_modelspec(
        "inputUnify.cropSize", default="227"))
    input_str = input_str.lower()
    if input_str == "none":
        return (None, None)
    size = input_str.split("x")
    try:
        if len(size) == 1:
            return (int(size[0]), int(size[0]))
        return (int(size[0]), int(size[1]))
    except ValueError as verr:
        logger.warn("ignored bad input crop_size=%s, err: %s", input_str, verr)
        return (None, None)


def get_sampleset_class_num(data_type="train"):
    """获取样本集的种类数目
    """
    return fetch_config_from_samplesetinfo("stats.numOfClasses", data_type=data_type, default=0)


def get_sampleset_num(data_type="train"):
    """获取样本集的数目
    """
    return fetch_config_from_samplesetinfo("stats.numOfSamples", data_type=data_type, default=0)


def get_job_id():
    job_name = os.getenv("JOB_NAME", "")
    try:
        job_id = job_name.split("-")[2]
    except IndexError:
        job_id = ""
    return job_id


def ceil_by_level(num, level=1):
    """ 按照位数取整

    Args:
        num:    数值
        level:  取整的倍数

    Returns:
        取整之后的数值
    """
    return int(math.ceil(float(num) / level) * level)
