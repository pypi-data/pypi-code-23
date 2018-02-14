# import unittest
from mtaf import mtaf_logging
from mtaf.user_exception import UserException as Ux, UserFailException as Fx
from mtaf.trace import Trace, TestCase, SkipTrace

log = mtaf_logging.get_logger('mtaf.wrapper_test')
mtaf_logging.console_handler.setLevel(mtaf_logging.INFO)
# Trace = SkipTrace


@Trace(log)
def f1(*args):
    return f2(args[0])


@Trace(log)
def f2(arg):
    if arg == 'a':
        return f3(arg)
    return f4(arg)


@Trace(log)
def f3(arg):
    raise Ux('f3 user exception here, arg=%s' % arg)


@Trace(log)
def f4(arg):
    l = []
    log.debug('causing a list index out of range error')
    return l[arg]


# class EsiTestCase(unittest.TestCase):
#     pass
    # failureException = Fx

run_list = ['test_1_trace_f3']


# def cb1(e, exc_info):
#     print "[1] got an exception: %s" % e
#
#
# def cb2(e, exc_info):
#     print "[2] got an exception: %s" % e


# class AClass(EsiTestCase):
#     val = None

f3('a')

    # @TestCase(log, run_list)
    # def test_2_trace_f1(self):
    #     f2(1)

    # @TestCase(log, run_list)
    # def test_3_trace_f1(self):
    #     # raise unittest.SkipTest('do not run this one')
    #     f1('a', 'b', 'c')

    # @TestCase(log, run_list)
    # def test_4_trace_f2(self):
    #     f1(1, 2, 3)
    #
    # @TestCase(log, run_list)
    # def test_5_is_gonna_fail(self):
    #     self.assertEqual('foo', 'bar', 'foo and bar are not equal')

    # @TestCase(log)
    # def test_4_is_gonna_throw_a_ux(self):
    #     raise Ux("had an exception on purpose")
    #
    # @TestCase(log)
    # def test_5_is_log_something_and_fail(self):
    #     # log.info('testing to see if foo and bar are equel')
    #     self.assertEqual('foo', 'bar', 'foo and bar are not equal')


# suite = unittest.TestSuite()
# suite.addTest(unittest.TestLoader().loadTestsFromTestCase(AClass))
# runner = unittest.TextTestRunner(verbosity=0, resultclass=TestResult)
# result = runner.run(suite)


