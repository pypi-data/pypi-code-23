import logging
import traceback
from copy import deepcopy
from time import sleep

from celery import group, chain, Celery
from celery.bin.control import inspect
from loader.function import load
from logcc.util.table import trace_table

from worker.util import grouper_it
from worker.thread import work as thread_work
from worker.coroutine import work as coroutine_work


def celery_coroutine_worker(self, data, info):
    sub_info = deepcopy(info)
    resp = coroutine_work(data, sub_info)
    return resp


def celery_thread_worker(self, data, info):
    sub_info = deepcopy(info)
    resp = thread_work(data, sub_info)
    return resp


celery_worker = celery_thread_worker


def parallel_chunked(data, info):
    func_str = info.get('celery_worker')
    func = load(func_str)
    tasks_data = []
    tasks = []
    for i, d in enumerate(data):
        for index, chunked_data in enumerate(grouper_it(d, info.get('chunk_size', 20))):
            # tasks_data.append(chunked_data)
            sig = func.s(chunked_data, info)
            tasks.append(sig)
    # print(tasks)
    callback = info.get('group_callback')
    if callback:
        callback = load(callback)
        return group(*tasks) | callback.s()
    g = group(tasks)
    return g


def wait_for_group(results, celery_sleep=None, callback=None):
    if callback:
        rs = results.results
        while 1:
            success = 0
            for r in rs:
                if r.successful():
                    success += 1
                else:
                    break
            if len(rs) == success:
                break
            if celery_sleep:
                sleep(celery_sleep)
    else:
        sleep(celery_sleep)


def final_results(results_list):
    final_results = []
    for results in results_list:
        rs = results.results
        for r in rs:
            final_results.append(r.result)
    return final_results


def work(data, info):
    celery_chunk_size = info.get('celery_chunk_size', 80)
    celery_max_workers = info.get('celery_max_workers', 4)
    celery_sleep = info.get('celery_sleep', 0.2)
    queue = info.get('queue', 'worker')
    callback = info.get('final_callback')
    splitted_data = []

    for index, data_chunked in enumerate(grouper_it(data, celery_chunk_size)):
        splitted_data.append(data_chunked)
    results_list = []
    for index, splitted_chunked in enumerate(grouper_it(splitted_data, celery_max_workers)):
        tasks = parallel_chunked(splitted_chunked, info)
        results = tasks.apply_async(queue=queue)
        wait_for_group(results, celery_sleep, callback)
        results_list.append(results)

    if callback:
        results = final_results(results_list)
        callback = load(callback)
        return callback(results)
    return results_list


app = Celery('worker', include=[
    'worker.celery_demo_tasks',
    'test.functional.test_celery',
])
app.config_from_object('worker.celeryconfig')

if __name__ == '__main__':
    app.start()
