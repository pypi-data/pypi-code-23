import functools
import traceback
import threading
import logging

class RetryNotPossible(Exception):
    pass


def _stubborn(delays):
    def decorator(f):
        @functools.wraps(f)
        def res(self, *args, **kwargs):
            if hasattr(self, 'log'):
                log = self.log.getChild('stubborn')
            else:
                log = logging.getLogger('stubbornness.stubborn')
    
            event = threading.Event()
            for delay in delays:
                try:
                    return f(self, *args, **kwargs)
                except RetryNotPossible:
                    raise
                except:
                    log.warning("{0} failed, retry in {1} sec\n{2}".format(f.__name__, delay, traceback.format_exc()))
                    event.wait(delay)
            return f(self, *args, **kwargs)
        return res
                                     
    return decorator


def stubborn(func = None, delays=[1, 2, 3]):
    '''
    should be used as
    @stubborn
    def my_func(...):

    or

    @stubborn(delays = [1, 5, 20])
    def my_func(....):
    '''
    if func is not None:
        return _stubborn(delays)(func)
    else:
        return _stubborn(delays)
        
