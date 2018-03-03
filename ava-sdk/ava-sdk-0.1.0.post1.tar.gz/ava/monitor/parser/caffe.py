#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import datetime
import stats
import extract_seconds


def parse(line):
    """解析caffe训练日志

    Args:
            line: 行粒度日志字符串

    Returns:
            IntervalTrainStats
    """

    regex_iteration = re.compile('Iteration (\d+)')
    regex_train_output = re.compile(
        'Train net output #(\d+): (\S+) = ([\.\deE+-]+)')
    regex_test_output = re.compile(
        'Test net output #(\d+): (\S+) = ([\.\deE+-]+)')
    regex_learning_rate = re.compile(
        'lr = ([-+]?[0-9]*\.?[0-9]+([eE]?[-+]?[0-9]+)?)')
    regex_loss = re.compile(
        'Iteration \d+.*, loss = ([-+]?[0-9]*\.?[0-9]+([eE]?[-+]?[0-9]+)?)')

    train_stats = stats.IntervalTrainStats()
    iteration_match = regex_iteration.search(line)
    if iteration_match:
        train_stats.iteration = int(iteration_match.group(1))

    """
    caffe中日志没有打印year，caffe自带的解析脚本是判断log文件的生成时间来决定year的...
    FIXME, 下面的方法在跨年的时候会有问题
    """
    now = datetime.datetime.now()
    try:
        train_stats.dt = extract_seconds.extract_datetime_from_line(
            line, now.year)
    except Exception as err:
        return train_stats

    learning_rate_match = regex_learning_rate.search(line)
    if learning_rate_match:
        train_stats.lr = float(learning_rate_match.group(1))

    loss_match = regex_loss.search(line)
    if loss_match:
        train_stats.loss = float(loss_match.group(1))

    train_net_output_match = regex_train_output.search(line)
    if train_net_output_match:
        name = train_net_output_match.group(2)
        if name == 'accuracy':
            train_stats.accuracy = float(train_net_output_match.group(3))

    # TODO 其它情况

    return train_stats
