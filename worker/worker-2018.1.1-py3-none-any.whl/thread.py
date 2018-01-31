import logging
import traceback
from concurrent import futures
from copy import deepcopy

from loader.function import load

from worker.util import grouper_it


def work(data, info):
    log = logging.getLogger('worker')
    results = []
    chunk_size = info.get('chunk_size', 20)
    max_workers = info.get('max_workers', 4)
    try:
        func_str = info.get('worker')
        func = load(func_str)
    except Exception as exc:
        log.error('dynamic worker func invalid! %s' % exc)
        return results

    Executor = futures.ThreadPoolExecutor
    for index, data_chunked in enumerate(grouper_it(data, chunk_size * max_workers)):
        with Executor(max_workers=max_workers) as executor:
            future_to_data = {}
            info = deepcopy(info)
            info['index'] = index
            log.info('thread worker chunk %d processing.' % (index))

            for i, data_chunked_sub in enumerate(grouper_it(data_chunked, chunk_size)):
                future_to_data[executor.submit(func, data_chunked_sub, info)] = data_chunked_sub

            for future in futures.as_completed(future_to_data):
                data = future_to_data[future]
                try:
                    result = future.result()
                except Exception as exc:
                    log.critical('exception catched! %s -- %r' % (exc, data))

                    traceback.print_tb(exc.__traceback__)
                else:
                    if result is None:
                        result = []
                    results.extend(result)
    return results
