# -*- coding: utf-8 -*-

import os
import sys
import threading
import traceback
import logging
from logging.handlers import RotatingFileHandler
from multiprocessing import Queue

# remove some packages' verbose debug log
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger()


def initialize_test_logger():
    """ 初始化 unittest logger 。 """
    logging.basicConfig(level=logging.DEBUG)


def initialize_logger(basedir, node=None, debug=False):
    """ 初始化 logger 。

    1. 格式化输出到标准流。格式化支持 Node[1] Node[3] 区分不同节点（分布式）的 worker 。
    2. 格式化输出到文件 <basedir>/run.log 。
    """

    # 默认值是 True，如果为 False 说明已经初始化过了。
    logger = logging.getLogger()

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    node_formatter = "" if node is None else "Node[%s] " % node
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] " +
                                  "[%(threadName)s/%(filename)s:%(lineno)s - %(funcName)s()] " + node_formatter + "%(message)s")
    raw_formatter = logging.Formatter("%(message)s")

    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = MultiProcessingLogHandler(
        os.path.join(basedir, "run.log"),
        maxBytes=(1048576 * 50), backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class MultiProcessingLogHandler(logging.Handler):
    """ 支持多进程的 LogHandler, 最终将 log 打入 RotatingFileHandler 中 """

    def __init__(self, filename, mode='w', maxBytes=0, backupCount=10):
        logging.Handler.__init__(self)

        self._handler = RotatingFileHandler(
            filename, mode, maxBytes, backupCount)
        self.queue = Queue(-1)

        log_thread = threading.Thread(target=self.receive)
        log_thread.daemon = True
        log_thread.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except Exception:
                traceback.print_exc(file=sys.stderr)

    def send(self, signal):
        self.queue.put_nowait(signal)

    def _format_record(self, record):
        """
        序列化 record 的 args 和 exc_info，
        尽量降低把错误和冗余信息丢进 pipe 的可能性。
        """
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        """ 实现 Handler 的 emit 方法，将消息丢进 queue 中 """
        try:
            signal = self._format_record(record)
            self.send(signal)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)
