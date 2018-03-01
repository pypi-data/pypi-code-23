# -*- coding: utf-8 -*-
import subprocess
import types
from ava.log.logger import logger


def logproc(proc, log_hook=None):
    """重定向 subprocess 的日志。

    1. 输出到当前的 logger
    2. （可选）对日志内容作处理

    Args:
        proc: A subprocess object.
        log_hook: One or multiple function(s). 对截取的每行日志处理分析。
    """
    with proc.stdout:
        for l in iter(proc.stdout.readline, b''):
            logger.info(l.strip())
            if log_hook is None:
                continue
            if isinstance(log_hook, types.FunctionType):
                log_hook(l)
                continue
            if isinstance(log_hook, types.ListType):
                for f in log_hook:
                    f(l)
                continue


def runproc(args, log_hook=None):
    """运行 subprocess 。

    1. 启动 subprocess 并处理日志。
    2. 等待运行结束。

    Args:
        args: Subprocess args.
        log_hook: One or multiple function(s). 对截取的每行日志处理分析。

    Returns:
        subprocess exit_code.
    """
    proc = startproc(args)
    logproc(proc, log_hook)
    exit_code = proc.wait()
    if exit_code > 0:
        logger.error("%s exit code: %d", args[0], exit_code)
    else:
        logger.info("%s exit code: %d", args[0], exit_code)
    return exit_code


def startproc(args):
    """启动 subprocess ，仅封装 subprocess。"""
    logger.info(" ".join(args))
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
