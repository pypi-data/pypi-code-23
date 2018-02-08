# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

import sys
from importlib import import_module
from optparse import OptionParser

from gm.__version__ import __version__
from gm.callback import callback_controller
from gm.constant import CSDK_OPERATE_SUCCESS, DATA_TYPE_TICK, \
    SUB_TAG, SCHEDULE_INFO

from gm.csdk.c_sdk import py_gmi_current, py_gmi_schedule, \
    py_gmi_set_data_callback, py_gmi_set_strategy_id, gmi_set_mode, \
    py_gmi_set_backtest_config, py_gmi_subscribe, py_gmi_set_token, \
    py_gmi_unsubscribe, \
    py_gmi_get_parameters, py_gmi_add_parameters, py_gmi_set_parameters, \
    py_gmi_log, py_gmi_strerror, py_gmi_run, py_gmi_set_timer, \
    py_gmi_set_serv_addr, gmi_live_init, gmi_poll
from gm.enum import MODE_UNKNOWN, ADJUST_NONE, MODE_BACKTEST
from gm.model.storage import context
from gm.model.sub import SubDetail
from gm.pb.common_pb2 import Logs
from gm.pb.data_pb2 import Ticks
from gm.pb.rtconf_pb2 import Parameters
from gm.pb.rtconf_service_pb2 import GetParametersReq
from gm.pb_to_dict import protobuf_to_dict
from gm.utils import load_to_list, load_to_second

running = True

def _unsubscribe_bar(symbol, frequency):
    [context.inside_remove_bar_sub(sub) for sub in context.inside_bar_subs if SUB_TAG.format(symbol, frequency) == sub.sub_tag]


def _unsubscribe_all():
    context.inside_unsubscribe_all()


def set_token(token):
    """
    设置用户的token，用于身份认证
    """
    py_gmi_set_token(token)
    context.token = str('bearer {}'.format(token))


def get_version():
    return __version__


def subscribe(symbols, frequency='1d', count=1, wait_group=False, wait_group_timeout='10s', unsubscribe_previous=False):
    """
    订阅行情，可以指定symbol， 数据滑窗大小，以及是否需要等待全部代码的数据到齐再触发事件。
    wait_group: 是否等待全部相同频度订阅的symbol到齐再触发on_bar事件。
    """
    if frequency.endswith('m'):
        frequency = '{}s'.format(int(frequency[0:-1]) * 60)

    symbols = load_to_list(symbols)
    symbols_str = ','.join(symbols)
    status = py_gmi_subscribe(symbols_str, frequency, unsubscribe_previous)
    if not status == CSDK_OPERATE_SUCCESS:
        return

    if unsubscribe_previous:
        _unsubscribe_all()

    # tick不进行缓存
    if frequency == DATA_TYPE_TICK:
        context.inside_tick_subs = context.inside_tick_subs.union(symbols)
        return

    # bar缓存初始化
    wait_group_timeout = load_to_second(wait_group_timeout)
    # count 必须大于2, 不然没法进行wait_group, 被冲掉了
    if count < 2:
        count = 2

    [context.inside_append_bar_sub(
        SubDetail(symbol, frequency, count, wait_group, wait_group_timeout,
                  unsubscribe_previous)) for symbol in symbols]


def unsubscribe(symbols, frequency='1d'):
    """
    unsubscribe - 取消行情订阅

    取消行情订阅，默认取消所有已订阅行情
    """
    symbols = load_to_list(symbols)
    symbols_str = ','.join(symbols)
    if frequency.endswith('m'):
        frequency = '{}s'.format(int(frequency[0:-1]) * 60)

    status = py_gmi_unsubscribe(symbols_str, frequency)
    if not status == CSDK_OPERATE_SUCCESS:
        return

    if symbols_str == '*':
        return _unsubscribe_all()

    if frequency == DATA_TYPE_TICK:
        context.inside_tick_subs = context.inside_tick_subs.difference(symbols)
        return

    [_unsubscribe_bar(symbol, frequency) for symbol in symbols]


def current(symbols, fields=''):
    """
    查询当前行情快照，返回tick数据
    """
    symbols = load_to_list(symbols)
    fields = load_to_list(fields)

    symbols_str = ','.join(symbols)
    fields_str = ','.join(fields)

    ticks = Ticks()
    status, data = py_gmi_current(symbols_str, fields_str)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    ticks.ParseFromString(data)
    ticks = [protobuf_to_dict(tick) for tick in ticks.data]
    if not fields:
        return ticks

    return ticks


def get_strerror(error_code):
    return py_gmi_strerror(error_code)


def schedule(schedule_func, date_rule, time_rule):
    """
    定时任务
    """
    schemdule_info = SCHEDULE_INFO.format(date_rule=date_rule, time_rule=time_rule)
    context.inside_schedules[schemdule_info] = schedule_func
    py_gmi_schedule(date_rule, time_rule)


def run(strategy_id='', filename='', mode=MODE_UNKNOWN, token='',
        backtest_start_time='',
        backtest_end_time='',
        backtest_initial_cash=1000000,
        backtest_transaction_ratio=1,
        backtest_commission_ratio=0,
        backtest_slippage_ratio=0,
        backtest_adjust=ADJUST_NONE,
        backtest_check_cache=1,
        serv_addr=''):
    """
    执行策略
    """

    parser = OptionParser()
    parser.add_option("--strategy_id", action="store",
                      dest="strategy_id",
                      default=strategy_id,
                      help="策略id")

    parser.add_option("--filename", action="store",
                      dest="filename",
                      default=filename,
                      help="策略文件名称")

    parser.add_option("--mode", action="store",
                      dest="mode",
                      default=mode,
                      help="策略模式选择")

    parser.add_option("--token", action="store",
                      dest="token",
                      default=token,
                      help="用户token")

    parser.add_option("--backtest_start_time", action="store",
                      dest="backtest_start_time",
                      default=backtest_start_time,
                      help="回测开始时间")

    parser.add_option("--backtest_end_time", action="store",
                      dest="backtest_end_time",
                      default=backtest_end_time,
                      help="回测结束时间")

    parser.add_option("--backtest_initial_cash", action="store",
                      dest="backtest_initial_cash",
                      default=backtest_initial_cash,
                      help="回测初始资金")

    parser.add_option("--backtest_transaction_ratio", action="store",
                      dest="backtest_transaction_ratio",
                      default=backtest_transaction_ratio,
                      help="回测交易费率")

    parser.add_option("--backtest_commission_ratio", action="store",
                      dest="backtest_commission_ratio",
                      default=backtest_commission_ratio,
                      help="回测成交比率")

    parser.add_option("--backtest_slippage_ratio", action="store",
                      dest="backtest_slippage_ratio",
                      default=backtest_slippage_ratio,
                      help="回测滑点费率")

    parser.add_option("--backtest_adjust", action="store",
                      dest="backtest_adjust",
                      default=backtest_adjust,
                      help="回测复权模式")

    parser.add_option("--backtest_check_cache", action="store",
                      dest="backtest_check_cache",
                      default=backtest_check_cache,
                      help="回测是否使用缓存")

    parser.add_option("--serv_addr", action="store",
                      dest="serv_addr",
                      default=serv_addr,
                      help="终端地址")

    (options, args) = parser.parse_args()
    strategy_id = options.strategy_id
    filename = options.filename
    mode = int(options.mode)
    token = options.token
    backtest_start_time = options.backtest_start_time
    backtest_end_time = options.backtest_end_time
    backtest_initial_cash = float(options.backtest_initial_cash)
    backtest_transaction_ratio = float(options.backtest_transaction_ratio)
    backtest_commission_ratio = float(options.backtest_commission_ratio)
    backtest_slippage_ratio = float(options.backtest_slippage_ratio)
    backtest_adjust = int(options.backtest_adjust)
    backtest_check_cache = int(options.backtest_check_cache)
    serv_addr = options.serv_addr


    from gm import api
    if filename.endswith(".py"):
        filename = filename[:-3]
    filename = filename.replace("/", ".")
    filename = filename.replace('\\', ".")
    fmodule = import_module(filename)

    for name in api.__all__:
        if name not in fmodule.__dict__:
            fmodule.__dict__[name] = getattr(api, name)

    # 服务地址设置
    if serv_addr:
        set_serv_addr(serv_addr)

    set_token(token)

    # 实时模式下 1000毫秒触发一次timer事件 用来处理wait_group的过期
    py_gmi_set_timer(1000)
    py_gmi_set_strategy_id(strategy_id)
    gmi_set_mode(mode)
    context.mode = mode
    context.strategy_id = strategy_id

    # 调用户文件的init
    context.inside_file_module = fmodule
    context.token = token
    context.backtest_start_time = backtest_start_time
    context.backtest_end_time = backtest_end_time
    context.adjust_mode = backtest_adjust
    py_gmi_set_data_callback(callback_controller)
    fmodule.init(context)

    if mode == MODE_BACKTEST:
        py_gmi_set_backtest_config(start_time=backtest_start_time,
                                   end_time=backtest_end_time,
                                   initial_cash=backtest_initial_cash,
                                   transaction_ratio=backtest_transaction_ratio,
                                   commission_ratio=backtest_commission_ratio,
                                   slippage_ratio=backtest_slippage_ratio,
                                   adjust=backtest_adjust,
                                   check_cache=backtest_check_cache
                                   )

        return py_gmi_run()

    if gmi_live_init():
        return

    while running:
        gmi_poll()


def get_parameters():
    req = GetParametersReq()
    req.owner_id = context.strategy_id
    req = req.SerializeToString()
    status, result = py_gmi_get_parameters(req)
    if not status == CSDK_OPERATE_SUCCESS:
        return []

    req = Parameters()
    req.ParseFromString(result)

    return [protobuf_to_dict(parameters) for parameters in req.parameters]


def add_parameter(key, value, min=0, max=0, name='',
                  intro='', group='', readonly=False):

    req = Parameters()
    req.owner_id = context.strategy_id
    parameter = req.parameters.add()
    parameter.key = key
    parameter.value = value
    parameter.min = min
    parameter.max = max
    parameter.name = name
    parameter.intro = intro
    parameter.group = group
    parameter.readonly = readonly
    req = req.SerializeToString()
    py_gmi_add_parameters(req)


def set_parameter(key, value, min=0, max=0, name='',
                  intro='', group='', readonly=False):

    req = Parameters()
    req.owner_id = context.strategy_id
    parameter = req.parameters.add()
    parameter.key = key
    parameter.value = value
    parameter.min = min
    parameter.max = max
    parameter.name = name
    parameter.intro = intro
    parameter.group = group
    parameter.readonly = readonly
    req = req.SerializeToString()
    py_gmi_set_parameters(req)


def log(level, msg, source):
    logs = Logs()
    log = logs.data.add()
    log.owner_id = context.strategy_id
    log.source = source
    log.level = level
    log.msg = msg

    req = logs.SerializeToString()
    py_gmi_log(req)


def stop():
    global running
    running = False
    sys.exit(2)

def set_serv_addr(addr):
    py_gmi_set_serv_addr(addr)