# -*- coding: utf-8 -*-

import os
import json
import pytest
import time
import datetime
from ava.monitor.probe.protocol import metric
from ava.monitor.probe.protocol import encode
from ava.monitor.probe import probe
from ava.monitor.parser import caffe as caffe_parser
from ava.monitor import config as monitor_config
from ava.monitor import caffe as caffe_monitor


def test_probe_metric_encode():
    m = metric.ProbeMetric()
    m.measurement = 'test-metric'
    m.tagk_list, m.tagv_list = ['tagk1'], ['tagv1']
    m.fieldk_list, m.fieldv_list = ['field1'], ['str1']
    assert(encode.encode(m) == 'test-metric,tagk1=tagv1 field1="str1"')

    m = metric.ProbeMetric()
    m.measurement = 'test-metric'
    m.tagk_list, m.tagv_list = ['tagk1'], ['tagv,1']
    m.fieldk_list, m.fieldv_list = ['field1'], [123]
    assert(encode.encode(m) == 'test-metric,tagk1=tagv\,1 field1=123')

    m = metric.ProbeMetric()
    m.measurement = 'test-metric'
    m.tagk_list, m.tagv_list = ['tagk=1'], ['tagv,1']
    m.fieldk_list, m.fieldv_list = ['field 1'], [True]
    assert(encode.encode(m) == 'test-metric,tagk\=1=tagv\,1 field\ 1=true')

    m = metric.ProbeMetric()
    m.measurement = 'm,= etric'
    m.tagk_list, m.tagv_list = ['tagk,= 1'], ['tagv,= "1']
    m.fieldk_list, m.fieldv_list = ['field 1'], [1.0]
    assert(encode.encode(m) == 'm\,=\ etric,tagk\,\=\ 1=tagv\,\=\ \"1 field\ 1=1.0')


def test_caffe_log_parser():
    log = """I0613 10:21:25.625161   252 data_layer.cpp:73] Restarting data prefetching from start."""
    s = caffe_parser.parse(log)
    assert(s.iteration == None)
    assert(s.dt != None)

    log = """I0613 10:21:25.756645   202 solver.cpp:397]     Test net output #0: accuracy = 0.1215"""
    s = caffe_parser.parse(log)
    assert(s.iteration == None)
    assert(s.dt != None)
    assert(s.accuracy == None)

    log = """I0613 10:21:25.756645   202 solver.cpp:397]     Train net output #0: accuracy = 0.1215"""
    s = caffe_parser.parse(log)
    assert(s.iteration == None)
    assert(s.dt != None)
    assert(s.accuracy == 0.1215)

    log = """I0613 10:21:26.202908   202 solver.cpp:218] Iteration 0 (-4.41298e+18 iter/s, 3.779s/100 iters), loss = 2.36947"""
    s = caffe_parser.parse(log)
    assert(isinstance(s.iteration, int) and s.iteration == 0)
    assert(s.dt.hour == 10 and s.dt.minute == 21 and s.dt.second == 26)
    assert(s.loss == 2.36947)

    log = """I0613 10:22:25.735756   202 solver.cpp:218] Iteration 100 (1.67977 iter/s, 59.532s/100 iters), loss = 0.232427"""
    s = caffe_parser.parse(log)
    assert(isinstance(s.iteration, int) and s.iteration == 100)
    assert(s.dt.hour == 10 and s.dt.minute == 22 and s.dt.second == 25)
    assert(s.loss == 0.232427)

    log = """I0613 10:38:57.579257   202 sgd_solver.cpp:105] Iteration 9900, lr = 0.00596843"""
    s = caffe_parser.parse(log)
    assert(isinstance(s.iteration, int) and s.iteration == 9900)
    assert(s.lr == 0.00596843)


def test_caffe_monitor():
    train_config = monitor_config.TrainConfig(
        job_type="training",
        job_id="1",
        training_sample_num=10000,
        batch_size=10,
        val_batch_size=8,
        batch_num_of_epoch=1000,
    )
    probe_config = probe.ProbeConfig(
        server_scheme="http",
        server_host="localhost",
        server_path="/v1/report/trainings/1/metric",
    )
    monitor = caffe_monitor.CaffeMonitor(train_config=train_config,
                                         probe_config=probe_config)

    log = """I0613 10:21:25.625161   252 data_layer.cpp:73] Restarting data prefetching from start."""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) == 0)

    log = """I0613 10:21:25.756645   202 solver.cpp:397]     Test net output #0: accuracy = 0.1215"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) == 0)

    log = """I0613 10:21:26.202908   202 solver.cpp:218] Iteration 0 (-4.41298e+18 iter/s, 3.779s/100 iters), loss = 2.36947"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_sample_metric = False
    for metric in metric_list:
        if metric.measurement == "ava_metric_training_sample_num":
            has_sample_metric = True
            break
        assert(check_metric_value(metric, "tag", "batch", 0))
    assert(has_sample_metric)
    dt = datetime.datetime.fromtimestamp(metric_list[0].time)
    assert(dt.hour == 10 and dt.minute == 21 and dt.second == 26)

    log = """I0623 10:47:43.812443    33 solver.cpp:218] Iteration 400 (12.4409 iter/s, 8.038s/100 iters), loss = 0.0306422"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_loss_metric = False
    for metric in metric_list:
        if metric.measurement == "ava_metric_training_loss":
            has_loss_metric = True
            assert(check_metric_value(metric, "tag", "epoch", 0))
            assert(check_metric_value(metric, "tag", "batch", 400))
            assert(check_metric_value(metric, "field", "value", 0.0306422))
            break

    assert(has_loss_metric)
    log = """I0623 10:47:44.812443    33 solver.cpp:218] Iteration 1400 (12.4409 iter/s, 8.038s/100 iters), loss = 0.0306422"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_loss_metric = False
    for metric in metric_list:
        if metric.measurement == "ava_metric_training_loss":
            has_loss_metric = True
            assert(check_metric_value(metric, "tag", "epoch", 1))
            assert(check_metric_value(metric, "tag", "batch", 1400))
            assert(check_metric_value(metric, "field", "value", 0.0306422))
            break
    assert(has_loss_metric)

    log = """I0613 10:38:57.579257   202 sgd_solver.cpp:105] Iteration 9900, lr = 0.00596843"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_lr_metric = False
    for metric in metric_list:
        if metric.measurement == "ava_metric_training_learning_rate":
            has_lr_metric = True
            assert(check_metric_value(metric, "tag", "epoch", 9))
            assert(check_metric_value(metric, "tag", "batch", 9900))
            assert(check_metric_value(metric, "field", "value", 0.00596843))
            break
    assert(has_lr_metric)

    # 对于同一个metric，需要iteration是递增的，否则将不会被解析
    log = """I0613 10:38:57.579257   202 sgd_solver.cpp:105] Iteration 9900, lr = 0.00596843"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) == 0)

    log = """I0613 10:39:08.560788   202 solver.cpp:310] Iteration 10000, loss = 0.0031008"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_loss_metric = False
    for metric in metric_list:
        if metric.measurement == "ava_metric_training_loss":
            has_loss_metric = True
            assert(check_metric_value(metric, "tag", "epoch", 10))
            assert(check_metric_value(metric, "tag", "batch", 10000))
            assert(check_metric_value(metric, "field", "value", 0.0031008))
            break
    assert(has_loss_metric)

    # 验证Iteration是否递增，前面已出现Iteration 10000，所以下面解析的batch仍为10000
    log = """I0613 10:38:57.579257   202 sgd_solver.cpp:105] Iteration 9901, lr = 0.00596843"""
    metric_list = monitor._parse_log(log)
    assert(len(metric_list) > 0)
    has_lr_metric = False
    for metric in metric_list:
        assert(check_metric_value(metric, "tag", "epoch", 10))
        assert(check_metric_value(metric, "tag", "batch", 10000))


def check_metric_value(metric, field_type, expect_name, expect_value):
    key_list, value_list = [], []
    if field_type == "tag":
        key_list = metric.tagk_list
        value_list = metric.tagv_list
    elif field_type == "field":
        key_list = metric.fieldk_list
        value_list = metric.fieldv_list
    else:
        print "invalid field_type: %s" % (field_type)
        return False

    if len(key_list) == 0 or len(value_list) == 0:
        return False
    try:
        name_idx = key_list.index(expect_name)
    except Exception:
        print "no %s in metric key_list, field_type: %s" % (expect_name, field_type)
        return False
    if value_list[name_idx] != expect_value:
        print "value[%s] != expect_value[%s], field_type: %s, name: %s" % (value_list[name_idx], expect_value, field_type, expect_name)
        return False
    return True
