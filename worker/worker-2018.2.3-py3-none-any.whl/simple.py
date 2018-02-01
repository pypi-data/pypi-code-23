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
    backup_info = deepcopy(info)
    for index, data_chunked in enumerate(grouper_it(data, chunk_size * max_workers)):
        log.debug('simple worker chunk %d processing.' % (index))
        if index == 0:
            index_mul = len(data_chunked) // chunk_size

        for i, data_chunked_sub in enumerate(grouper_it(data_chunked, chunk_size)):
            info = deepcopy(backup_info)
            info['index'] = index * index_mul + i
            try:
                result = func(data_chunked_sub, info)

            except Exception as exc:
                log.critical('exception catched! %s' % (exc))

                traceback.print_tb(exc.__traceback__)
            else:
                if result is None:
                    result = [None]
                results.extend(result)
    return results
