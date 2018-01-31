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
    for index, data_chunked in enumerate(grouper_it(data, chunk_size * max_workers)):
        info = deepcopy(info)
        info['index'] = index
        log.info('simple worker chunk %d processing.' % (index))
        try:
            result = func(data_chunked, info)

        except Exception as exc:
            log.critical('exception catched! %s' % (exc))

            traceback.print_tb(exc.__traceback__)
        else:
            if result is None:
                result = []
            results.extend(result)
    return results

