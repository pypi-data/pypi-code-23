import logging
import random
import asyncio
from copy import deepcopy
from datetime import datetime

from aiohttp import ClientSession
from loader.function import load
import traceback

# from worker.simple import work
from worker.util import grouper_it


async def test(data, info):
    # await asyncio.sleep(1)
    print(info)
    print(data)
    print('..................')
    # print(data.get('index'))
    return 'hello'


async def test2(data, info):
    # await asyncio.sleep(5)
    print(info.get('index'))
    print(data.get('index'))
    raise Exception('test2 e')
    return 'hello2'


async def test3(data, info):
    asyncio.sleep(random.randint(1, 3))
    print(info.get('index'))
    print(data.get('index'))
    print(data)
    print(info)
    return 'hello3'


async def bound_process(func, data, info):
    # Getter function with semaphore.
    async with info.get('semaphore'):
        response = await func(data, info)
    return response


# async def bound_process(data, info):
#     # Getter function with semaphore.
#     log = logging.getLogger('worker')
#     func_str = data.get('func') or info.get('func')
#     if func_str:
#         async with data.get('semaphore'):
#             try:
#                 func = load(func_str)
#             except Exception as exc:
#                 log.critical('exception catched! %s -- %r' % (exc, data))
#             else:
#                 response = await func(data, info)
#         return response
#     return None

async def _work(data, info):
    log = logging.getLogger('worker')
    chunk_size = info.get('chunk_size', 20)
    max_workers = info.get('max_workers', 4)
    max_sem = info.get('max_semaphore', len(data))
    try:
        func_str = info.get('worker')
        func = load(func_str)
    except Exception as exc:
        log.error('dynamic worker func invalid! %s' % exc)
        return None
    tasks = []
    semaphore = asyncio.Semaphore(max_sem)

    async with ClientSession() as session:
        backup_info = deepcopy(info)
        for index, data_chunked in enumerate(grouper_it(data, chunk_size * max_workers)):
            if index == 0:
                index_mul = len(data_chunked) // chunk_size
            for i, data_chunked_sub in enumerate(grouper_it(data_chunked, chunk_size)):
                info = deepcopy(backup_info)
                info['index'] = index * index_mul + i
                info['session'] = session
                info['semaphore'] = semaphore
                log.debug('coroutine worker chunk %d processing.' % (index))
                task = asyncio.ensure_future(bound_process(func, data_chunked_sub, info))
                tasks.append(task)
        try:
            gathers = asyncio.gather(*tasks, return_exceptions=True)
        except Exception as exc:
            log.critical('exception catched! %s -- %r' % (exc, data))
        else:
            response = await gathers
            return response


def work(data, info):
    log = logging.getLogger('worker')
    begin_time = datetime.now()

    response = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = asyncio.ensure_future(_work(data, info))
        response = loop.run_until_complete(tasks)
    except KeyboardInterrupt as exc:
        log.warning('keyboard exited! %s -- %r' % (exc, data))
        for task in asyncio.Task.all_tasks():
            task.cancel()
    finally:
        end_time = datetime.now()
        log.debug('coro done. time elapsed: {}'.format(end_time - begin_time))
    return response


if __name__ == '__main__':
    data = [
               {'hello': 'world'}
           ] * 4
    info = {
        'worker': 'test.pycurl.multicurl_simple',
    }
    resp = work(data, info)
    print(resp)
    # loop = asyncio.get_event_loop()
    # tasks = asyncio.ensure_future(coro([
    #                                        {'func': 'worker.coroutine.test'},
    #                                        {'func': 'worker.coroutine.test2'},
    #                                        {'func': 'worker.coroutine.test3'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                        # {'func': 'worker.pycurl.multicurl_simple'},
    #                                    ] * 200))
    # resp = loop.run_until_complete(tasks)
    # print(resp)
