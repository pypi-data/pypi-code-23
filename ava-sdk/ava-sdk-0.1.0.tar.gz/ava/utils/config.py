# -*- coding: utf-8 -*-
import csv
import hashlib
import json
from ava.utils.fileloc import file_location
from ava.log.logger import logger
from ava.utils.error import ConfigError


class Config(object):
    """ json 配置对象。 """

    # 缓存
    _cache = {}

    def __init__(self, fn):
        """初始化 Config 。

        Args:
            fn: 文件名。

        Raises:
            ConfigError: 读取文件异常。
        """
        self.conf = {}
        self.fn = fn
        try:
            with open(fn) as conf_file:
                self.conf = json.load(conf_file)
                logger.info("local conf: %s", json.dumps(self.conf, indent=2))
        except Exception as exp:
            msg = "bad or missing file '%s'" % self.fn
            raise ConfigError(msg)

    def get_key(self, key, is_required=False, default=None):
        """读取 key。

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

        Raises:
            ConfigError: 读取 key 异常。
        """
        conf = self.conf
        try:
            keys = key.split(".")
            for k in keys:
                conf = conf[k]
            logger.info("read from json conf '%s', get '%s = %s'",
                        self.fn, key, conf)
            return conf
        except Exception as exp:
            msg = "bad or missing key '%s' in '%s'" % (
                key, self.fn)
            if is_required:
                logger.error("%s, err: %s", msg, exp)
                raise ConfigError(msg)
            else:
                logger.info("use default %s, %s, err: %s", default, msg, exp)
                return default

    @staticmethod
    def cache_key(fn):
        """ 使用文件名 md5 作为缓存 key。"""
        md5 = hashlib.md5()
        md5.update(fn)
        return md5.hexdigest()

    @classmethod
    def new_config(cls, fn, use_cache=True):
        """ 封装缓存逻辑。 """
        key = cls.cache_key(fn)
        if use_cache and cls.cache_key(fn) in cls._cache:
            return cls._cache[key]
        conf = cls(fn)
        cls._cache.setdefault(cls.cache_key(fn), conf)
        return conf

    @classmethod
    def clear_cache(cls):
        """ 清除缓存。

        1. 全部清除。
        2. 只清除指定 key (TODO) 。
        """
        old = len(cls._cache)
        cls._cache.clear()
        logger.debug("Config cache cleared. %d cached -> %d cached",
                     old, len(cls._cache))


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def fetch_config_obj(workdir, config_type, use_str=True):
    fn = file_location(workdir, "config/%s" % config_type)
    obj = json.load(open(fn), encoding="utf-8")
    return byteify(obj) if use_str else obj


def fetch_config(workdir, config_type, key, is_required=False, default=None, use_cache=True):
    """ 封装 Config 类的使用。 """
    try:
        fn = file_location(workdir, "config/%s" % config_type)
        conf = Config.new_config(fn, use_cache)
    except Exception as err:
        if not is_required:
            return default
        else:
            raise err
    return conf.get_key(key, is_required=is_required, default=default)


def get_cores(workdir):
    """ 是否使用 GPU 及当前 worker 分配的 GPU 卡数。"""

    use_gpu = fetch_config(workdir, "trainingspec",
                           "resource.gpus", default=0) != 0
    # TODO 分布式情况下从 totalCores 读取当前训练使用的 GPU 数量是不准的，需要其他参数接口
    # gpus 指的是卡数，对应 cores 要根据卡的型号换算
    cores = fetch_config(workdir, "trainingspec",
                         "resource.gpus", default=1)
    return (use_gpu, cores)


def get_batch_size(workdir):
    """ 封装 batch_size 读取和计算。

    1. GPU 模式下 caffe/mxnet 真实训练batch_size 为 配置的训练batch_size * GPU 数量。
    2. GPU 模式下 caffe/mxnet 真实评估batch_size 为 配置的评估batch_size * GPU 数量。
    3. 评估 batch_size 未指定时默认为单核对应的 batch_size * GPU 数量。

    Args:
        workdir: 工作目录。

    Returns:
        (batch_size, actual_batch_size, val_batch_size)
        配置的『单核』batch_size，计算的真实 batch_size，评估 batch_size 。

    Raises:
        ConfigError: 配置异常。
    """
    batch_size = fetch_config(workdir, "trainingspec",
                              "solverOps.batchSize", is_required=True)
    use_gpu, cores = get_cores(workdir)
    logger.info("Cores GPU=%s, count=%d", use_gpu, cores)
    actual_batch_size = batch_size if not use_gpu else batch_size * cores
    val_batch_size = fetch_config(
        workdir, "trainingspec", "solverOps.valBatchSize", default=batch_size)
    if use_gpu:
        val_batch_size *= cores
    return (batch_size, actual_batch_size, val_batch_size)


def get_crop_size(workdir):
    """ 封装 crop_size 读取和计算。

    1. none/None/... ：不作剪裁。
    2. '123'： 剪裁正方形 123x123。
    3. '123x456'： 剪裁矩形 123(width)x456(height)
    4. 无法识别的 str ：不作剪裁

    Args:
        workdir: 工作目录。

    Returns:
        (crop_w, crop_h) 剪裁宽度，剪裁高度；全为 None 不剪裁。

    Raises:
        ConfigError: 配置异常。
    """
    input_str = str(fetch_config(workdir, "modelspec",
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


def get_mxnet_mean_values(workdir):
    """获取 MXNet mean file 内容
    file 格式为csv，字段分别为：mean_r, mean_g, mean_b

    Args:
        workdir: 工作目录

    Returns:
        (mean_r, mean_g, mean_b) RGB通道float值；全为 None 表示没有读取到数据
    """
    mean_r, mean_g, mean_b = None, None, None
    f = file_location(workdir, "mean.csv")
    rows = load_csv(f)
    if len(rows) < 1 or len(rows[0]) < 3:
        return (None, None, None)
    try:
        mean_r = float(rows[0][0])
        mean_g = float(rows[0][1])
        mean_b = float(rows[0][2])
        return (mean_r, mean_g, mean_b)
    except Exception as err:
        return (None, None, None)


def load_csv(filename):
    """
    load csv file into 2-dimesion list
    """
    try:
        arr = []
        with open(filename) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                arr.append(row)
        return arr
    except Exception as err:
        return []
