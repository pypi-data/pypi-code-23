import logging
import time
from functools import wraps

from logcc.util.table import trace_table as tt

from worker.exception import WorkerException


def grouper_it(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

# class WorkerWrapper(object):
#     def __init__(self, **kwargs):
#         self.__dict__.update(kwargs)
#
#     def __enter__(self):
#         self.start_time = time.time()
#         return self
#
#     def __exit__(self, typ, val, traceback):
#         self.end_time = time.time()
#         return self
#
#     def __call__(self, f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             with self:
#                 logger_name = self.__dict__.get('logger_name', 'worker')
#                 log = logging.getLogger(logger_name)
#                 try:
#                     ret = f(*args, **kwargs)
#                 except Exception as exc:
#                     print('....0......')
#                     tt(exc)
#                     print('....1......')
#                     log.critical('exception catched! %s %s' % (exc, type(exc)))
#                     print('....11......')
#                     print(self.end_time)
#                     log.debug("time elapsed: {}".format(self.end_time-self.start_time))
#                     print('....2......')
#                     return WorkerException('%s -- %r' % (type(exc), exc))
#                 else:
#
#                     log.debug("time elapsed: {}".format(self.end_time-self.start_time))
#                     return ret
#         return wrapper


# class log_runtime(ContextDecorator):
#     def __enter__(self):
#         self.start_time = time.time()
#         return self
#     def __exit__(self, typ, val, traceback):
#         # Note: typ, val and traceback will only be not None
#         # If an exception occured
#         print("{}: {}".format(self.label, time.time() - self.start_time))