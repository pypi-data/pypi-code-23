import time
import datetime as dt
import logging

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:  # fallback so that the imported classes always exist
    class ColorFallback():
        __getattr__ = lambda self, name: ''
    Fore = Back = Style = ColorFallback()

logging.getLogger(__name__).addHandler(logging.NullHandler())

def timmy(function, *args, **kwargs):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time()
        ms = (t2-t1)*1000.0

        pre_string = '[{}]'.format(__name__)
        func_string = '{0}({1}{2})'.format(function.__name__, args, kwargs)
        time_string = '{:.2f}ms'.format(ms)
        logging.debug('{}{}{}'.format(pre_string, func_string, time_string))
        return result
    return wrapper


def timmyprint(function, *args, **kwargs):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time()
        ms = (t2-t1)*1000.0

        pre_string = '[{}]'.format(__name__)
        func_string = '{0}({1}{2})'.format(function.__name__, args, kwargs)
        time_string = '{:.2f}ms'.format(ms)
        print(Fore.CYAN+pre_string,func_string,Fore.GREEN+time_string)
        return result
    return wrapper

# shorter alias for print
timmyp = timmyprint
