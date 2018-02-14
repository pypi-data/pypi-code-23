import inspect
import sys
import traceback
from time import time
import mtaf_logging
from appium import webdriver

from user_exception import UserException as Ux, UserFailException as Fx, UserTimeoutException as Tx, \
    stat_prefix as sp

log = mtaf_logging.get_logger('mtaf.wrappers')


# decorator for test cases that puts the test method name in log messages
# that are generated within a test method, and catches Ux exceptions to put
# the message in a "fail" call that unittest will display
class TestCase(object):

    def __init__(self, logger=None, run_list=None, except_cb=None):
        self.run_list = run_list
        self.logger = logger
        self.except_cb = except_cb

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            name = args[0]._testMethodName
            if self.run_list is not None and name not in self.run_list:
                args[0].skipTest('test in skip list')
            else:
                try:
                    with mtaf_logging.msg_src_cm(name):
                        return Trace(self.logger, self.except_cb)(f)(*args, **kwargs)
                except Ux as e:
                    args[0].fail(e.text)
        return wrapped


# spaces = 0

class Trace(object):

    def __init__(self, logger=None, except_cb=None, log_level='trace'):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.logger = logger
        self.except_cb = except_cb
        self.log_level = log_level

    @staticmethod
    def prefix():
        indent = mtaf_logging.trace_indent
        return 'TRACE%d:%s' % (indent, ' '*indent)

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """

        def wrapped_f(*args, **kwargs):
            # global spaces
            if self.logger is None:
                logger = log
            else:
                logger = self.logger
            log_fn = {
                'warn': logger.warn,
                'info': logger.info,
                'trace': logger.trace,
                'debug': logger.debug
            }[self.log_level]
            arg_reprs = []
            for arg in args:
                if type(arg) == webdriver.webelement.WebElement:
                    arg_reprs.append('<%s>' % arg._id)
                elif arg.__class__.__name__[-4:] == 'View':
                    arg_reprs.append(arg.__class__.__name__)
                else:
                    arg_reprs.append(repr(arg))
            for key in kwargs:
                arg = kwargs[key]
                if type(arg) == webdriver.webelement.WebElement:
                    arg_reprs.append('%s=<%s>' % (key, arg._id))
                elif arg.__class__.__name__[-4:] == 'View':
                    arg_reprs.append('%s=%s' % (key, arg.__class__.__name__))
                else:
                    arg_reprs.append('%s=%s' % (key, repr(arg)))

            called = "%s%s" % (f.func_name, '(%s)' % ','.join(arg_reprs))
            log_fn("%s %s" % (self.prefix(), called))
            mtaf_logging.trace_indent += 1
            retval = None
            self.elapsed_time = 0.0
            start_time = time()
            try:
                retval = f(*args, **kwargs)
                self.elapsed_time = time() - start_time
            except Fx as e:
                self.elapsed_time = time() - start_time
                logger.warn(('%%s %%s%%-%ds FAIL - %%s' % (35 - mtaf_logging.trace_indent))
                            % (self.prefix(), f.func_name, sp(), e.get_msg()))
                raise Fx('calling %s' % f.func_name)
            except Tx as e:
                self.elapsed_time = time() - start_time
                logger.warn(('%%s %%s%%-%ds FAIL - %%s' % (35 - mtaf_logging.trace_indent))
                            % (self.prefix(), f.func_name, sp(), e.get_msg()))
                raise Tx('User timeout exception: calling %s' % f.func_name)
            except KeyboardInterrupt:
                log.warn("got keyboard interrupt")
                raise
            except Exception as e:
                self.elapsed_time = time() - start_time
                (exc_type, value, tb) = sys.exc_info()
                tb_array = traceback.extract_tb(tb)
                if exc_type == Ux:
                    logger.warn(('%%s %%-%ds EXCEPTION:      %%s: %%s' % (35 - mtaf_logging.trace_indent))
                                % (self.prefix(), f.func_name, value.__class__.__name__, value.text))
                elif len(tb_array) < 2:
                    logger.warn(('%%s %%-%ds EXCEPTION:      %%s: %%s' % (35 - mtaf_logging.trace_indent))
                                % (self.prefix(), f.func_name, value.__class__.__name__, value.message))
                else:
                    logger.warn(('%%s %%-%ds EXCEPTION:      %%s: %%s [%%s]' % (35 - mtaf_logging.trace_indent))
                                % (self.prefix(), f.func_name, value.__class__.__name__,
                                   '%s line %s in %s attempting "%s"' % tb_array[1], value))

                if self.except_cb:
                    try:
                        self.except_cb(exc_type, value, tb)
                    except:
                        pass
                raise Ux('%s: calling %s from %s' % (value, f.func_name, "%s:%s" % tuple(inspect.stack()[1][1:3])),
                         sp=False)
            finally:
                mtaf_logging.trace_indent -= 1
                val_reprs = []
                if retval is None:
                    log_fn('%s %s returned [%.3fs]' % (self.prefix(), f.func_name, self.elapsed_time))
                else:
                    if type(retval) == list:
                        for val in retval:
                            if type(val) == webdriver.webelement.WebElement:
                                val_reprs.append('<%s>' % val._id)
                            else:
                                val_reprs.append(repr(val))
                        returned = '[%s]' % ','.join(val_reprs)
                    else:
                        if type(retval) == webdriver.webelement.WebElement:
                            returned = '<%s>' % retval._id
                        else:
                            returned = repr(retval)
                    if len(returned) > 160:
                        returned = returned[:160] + "..."
                    log_fn('%s %s returned %s [%.3fs]' % (self.prefix(), f.func_name, returned, self.elapsed_time))
            return retval
        return wrapped_f


# for debugging, set Trace = SkipTrace to avoid stepping into the Trace wrapper
class SkipTrace(Trace):
    def __init__(self, *args, **kwargs):
        super(SkipTrace, self).__init__(*args, **kwargs)
    def __call__(self, f):
        return f


def fake(func):
    def wrapper(context, *args, **kwargs):
        if 'fake' in str(context._config.tags).split(','):
            pass
            # sleep(0.1)
        else:
            func(context, *args, **kwargs)
    return wrapper

