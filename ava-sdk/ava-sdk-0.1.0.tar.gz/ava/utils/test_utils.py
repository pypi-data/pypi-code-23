# -*- coding: utf-8 -*-

import os
import json
import pytest
import time
import datetime
import csv
import ava.utils.fileloc as fileloc
import ava.utils.config as config
import ava.utils.uploader as uploader
import ava.utils.tool as tool
import ava.utils.cmd as cmd
import ava.utils.compress as compress
import ava.utils.utils as utils
from ava.log.logger import initialize_test_logger


@pytest.fixture
def workdir():
    initialize_test_logger()
    workdir = "testrun"
    fileloc.rm_path(workdir)
    return workdir


def dump_config_fixtures(conf, workdir, rpath, clear_cache=False):
    path = os.path.join(workdir, rpath)
    pdir = os.path.dirname(path)
    fileloc.mkdir_p(pdir)
    with open(path, 'w') as output:
        json.dump(conf, output, indent=2)
    if clear_cache:
        config.Config.clear_cache()
    return path


def test_fileloc(workdir):
    # data
    fn1 = dump_config_fixtures({}, workdir, "data/train/mean.csv")
    fn2 = dump_config_fixtures({}, workdir, "data/train/cache/data.rec")
    assert fileloc.file_location(workdir, "mean.csv") == fn1
    assert fileloc.file_location(workdir, "train.rec") == fn2
    fn3 = dump_config_fixtures({}, workdir, "data/train/cache/anything.mdb")
    assert fileloc.file_location(
        workdir, "train.lmdb") == os.path.dirname(fn3)
    # output & internal outputs
    assert fileloc.file_location(workdir, "hehe.log") == os.path.join(
        workdir, "run/logs/hehe.log")
    assert os.path.exists(os.path.join(workdir, "run/logs"))
    assert fileloc.file_location(workdir, "snapshot") == os.path.join(
        workdir, "run/output/snapshot")
    assert os.path.exists(os.path.join(workdir, "run/output"))
    assert fileloc.file_location(workdir, "fixed_train.prototxt") == os.path.join(
        workdir, "run/prepared/fixed_train.prototxt")
    assert os.path.exists(os.path.join(workdir, "run/prepared"))
    # model
    fn4 = dump_config_fixtures({}, workdir, "model/1.train.prototxt")
    fn5 = dump_config_fixtures({}, workdir, "model/weight.caffemodel")
    fn6 = dump_config_fixtures({}, workdir, "model/1.train.symbol.json")
    assert fileloc.file_location(workdir, "train.prototxt") == fn4
    assert fileloc.file_location(workdir, "weight.caffemodel") == fn5
    assert fileloc.file_location(workdir, "train.symbol.json") == fn6
    assert fileloc.file_location(workdir, "weight.params") is None
    fn7 = dump_config_fixtures({}, workdir, "model/weight.params")
    assert fileloc.file_location(workdir, "weight.params") == fn7
    # mean file，考虑优先级
    fn8 = dump_config_fixtures({}, workdir, "data/mean.binaryproto")
    fn9 = dump_config_fixtures({}, workdir, "model/mean.binaryproto")
    assert fileloc.file_location(workdir, "mean.binaryproto") == fn9
    fn10 = dump_config_fixtures({}, workdir, "data/mean.csv")
    fn11 = dump_config_fixtures({}, workdir, "model/mean.csv")
    assert fileloc.file_location(workdir, "mean.csv") == fn11


def test_config_cls(workdir):
    fn = dump_config_fixtures(
        {"key1": 1, "key2": {"key3": 2}}, workdir, "test.conf")
    conf = config.Config.new_config(fn)
    assert conf.get_key("key1") == 1
    assert conf.get_key("key2.key3") == 2
    assert conf.get_key("key1.key4") is None
    assert conf.get_key("key4.key5") is None
    assert conf.get_key("key4.key5", default=3) == 3
    with pytest.raises(config.ConfigError):
        conf.get_key("key4.key5", is_required=True)
    # test cache
    dump_config_fixtures(
        {"key1": 1, "key2": {"key3": 3}}, workdir, "test.conf")
    conf2 = config.Config.new_config(fn)
    assert conf2.get_key("key2.key3") == 2
    conf3 = config.Config.new_config(fn, use_cache=False)
    assert conf3.get_key("key2.key3") == 3
    dump_config_fixtures(
        {"key1": 1, "key2": {"key3": 4}}, workdir, "test.conf")
    config.Config.clear_cache()
    conf4 = config.Config.new_config(fn)
    assert conf4.get_key("key2.key3") == 4


def test_config_batch_size(workdir):
    def setup(input1, input2):
        dump_config_fixtures({"solverOps": input1,
                              "resource": input2}, workdir, "config/trainingspec", True)
    solverOpsBoth = {
        "batchSize": 64,
        "valBatchSize": 16,
    }
    solverOpsBatchOnly = {
        "batchSize": 64,
    }
    solverOpsNone = {
    }
    # TODO change with config logic
    resourceCPUNone = {
        "cpuCores": 0,
    }
    resourceCPU2 = {
        "cpuCores": 2,
        "gpus": 0
    }
    resourceGPUNone = {
        "gpus": 0,
    }
    resourceGPU1 = {
        "gpus": 1,
    }
    resourceGPU4 = {
        "gpus": 4,
    }

    setup(solverOpsBoth, resourceCPUNone)
    assert config.get_batch_size(workdir) == (64, 64, 16)
    setup(solverOpsBoth, resourceCPU2)
    assert config.get_batch_size(workdir) == (64, 64, 16)
    setup(solverOpsBoth, resourceGPUNone)
    assert config.get_batch_size(workdir) == (64, 64, 16)
    setup(solverOpsBoth, resourceGPU1)
    assert config.get_batch_size(workdir) == (64, 64, 16)
    setup(solverOpsBoth, resourceGPU4)
    assert config.get_batch_size(workdir) == (64, 64 * 4, 16 * 4)
    setup(solverOpsBatchOnly, resourceCPUNone)
    assert config.get_batch_size(workdir) == (64, 64, 64)
    setup(solverOpsBatchOnly, resourceGPU4)
    assert config.get_batch_size(workdir) == (64, 64 * 4, 64 * 4)
    with pytest.raises(config.ConfigError):
        setup(solverOpsNone, resourceCPUNone)
        config.get_batch_size(workdir)


def test_config_crop_size(workdir):
    def setup(input_str):
        dump_config_fixtures(
            {"inputUnify": {"cropSize": input_str}}, workdir, "config/modelspec", True)

    def setup_empty():
        dump_config_fixtures(
            {"inputUnify": {}}, workdir, "config/modelspec", True)

    crop_size_none1 = "None"
    crop_size_none2 = "none"
    crop_size_bad = "nonen"
    crop_size_int = 1
    crop_size_square1 = "222"
    crop_size_square2 = "222.1"
    crop_size_rect1 = "100x200"
    crop_size_rect2 = "100X200"
    crop_size_rect3 = "100*200"
    crop_size_rect4 = "100x 200"
    crop_size_rect5 = "100.1x200"

    setup_empty()
    assert config.get_crop_size(workdir) == (227, 227)
    setup(crop_size_none1)
    assert config.get_crop_size(workdir) == (None, None)
    setup(crop_size_none2)
    assert config.get_crop_size(workdir) == (None, None)
    setup(crop_size_bad)
    assert config.get_crop_size(workdir) == (None, None)
    setup(crop_size_int)
    assert config.get_crop_size(workdir) == (1, 1)
    setup(crop_size_square1)
    assert config.get_crop_size(workdir) == (222, 222)
    setup(crop_size_square2)
    assert config.get_crop_size(workdir) == (None, None)
    setup(crop_size_rect1)
    assert config.get_crop_size(workdir) == (100, 200)
    setup(crop_size_rect2)
    assert config.get_crop_size(workdir) == (100, 200)
    setup(crop_size_rect3)
    assert config.get_crop_size(workdir) == (None, None)
    setup(crop_size_rect4)
    assert config.get_crop_size(workdir) == (100, 200)
    setup(crop_size_rect5)
    assert config.get_crop_size(workdir) == (None, None)


def test_ceil_by_level():
    assert utils.ceil_by_level(123, 100) == 200
    assert utils.ceil_by_level(456, 100) == 500
    assert utils.ceil_by_level(123, 10) == 130


def make_csv_file(abs_filename, data):
    with open(abs_filename, 'w') as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerows(data)


def test_load_csv(workdir):
    fileloc.mkdir_p(workdir)

    filename = os.path.join(workdir, "test.csv")
    data = [(0.1, 0.2, 0.3)]
    make_csv_file(filename, data)
    ret_data = config.load_csv(filename)
    assert len(ret_data) == 1
    assert ret_data[0][0] == "0.1"
    assert ret_data[0][1] == "0.2"
    assert ret_data[0][2] == "0.3"

    data = [(0.1, 0.2, 0.3), (0.4, 0.5, 0.6)]
    make_csv_file(filename, data)
    ret_data = config.load_csv(filename)
    assert len(ret_data) == 2
    assert ret_data[0][0] == "0.1"
    assert ret_data[0][1] == "0.2"
    assert ret_data[0][2] == "0.3"
    assert ret_data[1][0] == "0.4"
    assert ret_data[1][1] == "0.5"
    assert ret_data[1][2] == "0.6"


def test_get_mxnet_mean_values(workdir):
    fileloc.mkdir_p(os.path.join(workdir, "model"))

    filename = os.path.join(workdir, "model", "mean.csv")
    data = [(0.1, 0.2, 0.3)]
    make_csv_file(filename, data)
    mean_r, mean_g, mean_b = config.get_mxnet_mean_values(workdir)
    assert mean_r == 0.1
    assert mean_g == 0.2
    assert mean_b == 0.3

    filename = os.path.join(workdir, "model", "mean.csv")
    data = [(0.1, 0.2, 0.3, 0.4)]
    make_csv_file(filename, data)
    mean_r, mean_g, mean_b = config.get_mxnet_mean_values(workdir)
    assert mean_r == 0.1
    assert mean_g == 0.2
    assert mean_b == 0.3

    filename = os.path.join(workdir, "model", "mean.csv")
    data = [(0.1, 0.2)]
    make_csv_file(filename, data)
    mean_r, mean_g, mean_b = config.get_mxnet_mean_values(workdir)
    assert mean_r == None
    assert mean_g == None
    assert mean_b == None


def test_tar_files(workdir):
    input_dir = os.path.join(workdir, "tar_input")
    output_file = os.path.join(workdir, "output.tar.gz")
    output_dir = os.path.join(workdir, "tar_output")
    fileloc.mkdir_p(input_dir)
    fileloc.mkdir_p(os.path.join(input_dir, "sub_dir"))
    file_a = os.path.join(input_dir, "a.txt")
    dir_a = os.path.join(input_dir, "sub_dir")
    file_b = os.path.join(dir_a, "b.txt")
    with open(file_a, "w") as f:
        f.write("a")
    with open(file_b, "w") as f:
        f.write("b")

    """
        a.txt
        sub_dir
            b.txt
    """
    assert compress.tar_files([file_a, dir_a], output_file) == None
    assert os.path.exists(os.path.join(output_file))
    assert compress.untar_file(output_file, output_dir) == None
    output_file_a = os.path.join(output_dir, "a.txt")
    assert os.path.exists(output_file_a)
    with open(file_a, "r") as f:
        content = f.read()
        assert content == "a"
    output_file_b = os.path.join(output_dir, "sub_dir", "b.txt")
    assert os.path.exists(output_file_b)
    with open(file_b, "r") as f:
        content = f.read()
        assert content == "b"

    fileloc.rm_path(output_file)
    fileloc.rm_path(output_dir)

    """
        a.txt
        b.txt
    """
    assert compress.tar_files([file_a, file_b], output_file) == None
    assert os.path.exists(os.path.join(output_file))
    assert compress.untar_file(output_file, output_dir) == None
    output_file_a = os.path.join(output_dir, "a.txt")
    assert os.path.exists(output_file_a)
    output_file_b = os.path.join(output_dir, "sub_dir", "b.txt")
    assert not os.path.exists(output_file_b)
    output_file_b = os.path.join(output_dir, "b.txt")
    assert os.path.exists(output_file_b)
