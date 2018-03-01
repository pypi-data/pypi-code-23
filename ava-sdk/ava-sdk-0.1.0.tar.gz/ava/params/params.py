# -*- coding: utf-8 -*-
import json
from ava.log.logger import logger
from ava.utils.config import Config
from ava.env import environment


def fetch_config_from_file(filepath, key, is_required=False, default=None, use_cache=True):
    try:
        conf = Config.new_config(filepath, use_cache)
    except Exception as err:
        if not is_required:
            return default
        else:
            raise err
    return conf.get_key(key, is_required=is_required, default=default)


def get_all():
    """获取训练params所有数据

    Returns:
        params: 解析配置文件的 dict，如果解析失败，返回空 dict
    """
    try:
        env = environment.Environment()
        with open(env.params_file) as f:
            params = json.load(f)
    except Exception:
        params = {}
    return params


def get_value(key, is_required=False, default=None, use_cache=True):
    """获取训练params信息

        key 以 '.' 分割，例如 'solverOps.solverPolicy.stepvalue' 代表
        {
            ...
            'solverOps': {
                'solverPolicy': {
                    'stepvalue': <value>
                }
            }
        }

        Args:
            key: 以 '.' 分割的配置名称。
            is_required: key 不存在时异常。
            default: key 不存在时返回默认值。

        Returns:
            配置文件中 key 对应的内容。
    """
    env = environment.Environment()
    return fetch_config_from_file(env.params_file, key, is_required=is_required, default=default, use_cache=use_cache)
