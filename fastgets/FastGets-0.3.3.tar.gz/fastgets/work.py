# coding: utf8

import sys
import os
import threading
import time

from fastgets import env
from fastgets.core import config_parse
from fastgets.core.errors import CrawlError, ProcessError
from fastgets.core.client import get_client
from fastgets.core.log import logger
from fastgets.pool import CrawlErrorPool, ProcessErrorPool, PendingPool, RunningPool
from fastgets.stats import InstanceStats, ClusterStats
from fastgets.utils import get_current_inner_ip, get_thread_name, format_exception


inner_ip = get_current_inner_ip()


def finish(task):
    InstanceStats.set_task_active(task.instance_id)

    start_time = time.time()

    logger.info('[crawl][{}][{}][start]'.format(task.func_name, task.url))
    try:
        page_raw = task.crawl()
        if not page_raw:
            return
    except CrawlError as e:
        task.crawl_error_traceback = e.traceback
        CrawlErrorPool.add(task)

        with get_client().pipeline() as pipe:
            RunningPool.remove(task, pipe=pipe)
            ClusterStats.incr('crawl_error', pipe=pipe)
            InstanceStats.incr(task.instance_id, 'crawl_error', pipe=pipe)
            pipe.execute()

        logger.error('[crawl][{}][{}][{}]'.format(task.func_name, task.url, e.traceback))
        return False
    else:
        logger.info('[crawl][{}][{}][finish][seconds: {}]'.format(task.func_name, task.url, time.time() - start_time))

    mid_time = time.time()

    logger.info('[process][{}][{}][start]'.format(task.func_name, task.url))
    try:
        task.process(page_raw)
    except ProcessError as e:
        task.page_raw = page_raw
        task.process_error_traceback = e.traceback

        ProcessErrorPool.add(task)

        with get_client().pipeline() as pipe:
            RunningPool.remove(task, pipe=pipe)
            ClusterStats.incr('process_error', pipe=pipe)
            InstanceStats.incr(task.instance_id, 'process_error', pipe=pipe)
            pipe.execute()
        logger.error('[process][{}][{}][{}]'.format(task.func_name, task.url, e.traceback))
        return False
    else:
        logger.info('[process][{}][{}][finish][seconds: {}]'.format(
            task.func_name, task.url, time.time() - mid_time
        ))

    end_time = time.time()

    task.crawl_seconds = mid_time - start_time
    task.process_seconds = end_time - mid_time

    with get_client().pipeline() as pipe:
        ClusterStats.incr('success', pipe=pipe)
        InstanceStats.incr(task.instance_id, 'success', pipe=pipe)
        InstanceStats.add_task_for_time_cost(task, pipe=pipe)
        RunningPool.remove(task, pipe=pipe)
        pipe.execute()


def run():
    from fastgets.models import Instance, UnknownError  # 确保读取 config 后再连接 MongoDB

    logger.info('worker start')
    while 1:
        try:
            ClusterStats.add_thread('{}_{}'.format(inner_ip, get_thread_name()))
            ClusterStats.add_server(inner_ip)

            finish_num = 0
            for instance_id in Instance.get_running_ids():
                task = PendingPool.fetch(instance_id)
                if not task:
                    continue

                if InstanceStats.check_rate_limit(instance_id, task.second_rate_limit):
                    task.add(reason=task.REASON_RATE_LIMIT)
                    RunningPool.remove(task)
                    continue

                finish(task)

                finish_num += 1

            if finish_num == 0:
                # logger.info('worker is sleeping...')
                time.sleep(1)
        except Exception:
            UnknownError.add(format_exception())
            time.sleep(60)  # 需要 sleep 较长时间，否则会把 mongodb 打爆


def main():
    env.mode = env.WORK
    config_parse()

    sys.path.insert(0, env.PROJECT_ROOT_DIR)

    for i in range(10):
        time.sleep(0.1)
        t = threading.Thread(target=run)
        t.start()


if __name__ == '__main__':
    main()
