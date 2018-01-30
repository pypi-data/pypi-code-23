# coding: utf8

import datetime
import threading
import time

from fastgets.models.instance import Instance
from .. import env
from ..core.errors import ProcessError, CrawlError
from ..core.log import logger
from ..pool import PendingPool
from ..stats import InstanceStats
from ..utils import create_id, format_exception
# from ..worker import finish
from ..writer import current_writers


class LocalEngine(object):

    def __init__(self, template_class, is_testing=False):
        logger.info('engine start on {} mode'.format(env.mode))

        self.template_class = template_class
        self.is_testing = is_testing
        if self.is_testing:
            self.thread_num = 1
        else:
            self.thread_num = self.template_class.config.get('thread_num', 5)
        self.instance = self.make_mock_instance()
        env.instance_id = self.instance.id

        self.seed_task_load_thread = None
        self.work_thread_list = []
        self.running_status_list = [False] * self.thread_num

    @classmethod
    def make_mock_instance(cls):
        instance = Instance()
        instance.id = create_id()
        return instance

    def start_seed_task_load_thread(self):

        def _():
            logger.info('load thread start')
            try:
                self.template_class.load()
            except Exception as e:
                # 框架层出错 需要让用户立即知道 并停止当前所有抓取过程
                self.instance.stop_at = datetime.datetime.now()
                raise e

        self.seed_task_load_thread = threading.Thread(target=_, daemon=True)
        self.seed_task_load_thread.start()

    def start_work_thread_list(self):

        def _(i):
            logger.debug('work thread start')
            while not self.instance.stop_at:
                try:
                    task = PendingPool.fetch(self.instance.id)
                    if task:
                        self.running_status_list[i] = True
                        if InstanceStats.check_rate_limit(self.instance.id, task.second_rate_limit):
                            task.add(reason=task.REASON_RATE_LIMIT)
                            self.running_status_list[i] = False
                        else:
                            try:
                                finish(task)
                            except CrawlError as e:
                                logger.error('[crawl][{}][{}][{}]'.format(task.func_name, task.url, format_exception()))
                                if self.is_testing:
                                    raise e
                            except ProcessError as e:
                                logger.error('[process][{}][{}][{}]'.format(task.func_name, task.url, format_exception()))
                                if self.is_testing:
                                    raise e
                            except Exception as e:
                                raise e
                            finally:
                                self.running_status_list[i] = False
                    else:
                        logger.debug('work thread is sleeping...')
                        time.sleep(1)
                except Exception as e:
                    self.running_status_list[i] = False
                    self.instance.stop_at = datetime.datetime.now()
                    raise e

        for i in range(self.thread_num):
            # self.running_status_list[i] = True
            work_thread = threading.Thread(target=_, args=(i, ), daemon=True)
            work_thread.start()
            self.work_thread_list.append(work_thread)

    def is_running(self):
        if self.instance.stop_at:
            # 因为异常主动停止
            return False

        if self.seed_task_load_thread.is_alive():
            return False

        return any(self.running_status_list) or PendingPool.get_current_task_num(self.instance.id)

    def run(self):
        self.start_seed_task_load_thread()
        time.sleep(1)  # 保证种子任务先加入队列 再启动work线程
        self.start_work_thread_list()

        while self.is_running():
            time.sleep(0.1)  # 需要短一点 框架层出错时可以尽快停止

        time.sleep(2)  # 等待可能的异常输出

        for writer in current_writers:
            writer.save()


def finish(task):

    start_time = time.time()

    logger.info('[crawl][{}][{}][start]'.format(task.func_name, task.url))
    page_raw = task.crawl()
    logger.info(
        '[crawl][{}][{}][finish][seconds: {}]'.format(task.func_name, task.url, time.time() - start_time))

    mid_time = time.time()

    logger.info('[process][{}][{}][start]'.format(task.func_name, task.url))
    task.process(page_raw)
    logger.info('[process][{}][{}][finish][seconds: {}][pending_pool:{}]'.format(
        task.func_name, task.url, time.time() - mid_time, PendingPool.get_current_task_num(task.instance_id)
    ))
