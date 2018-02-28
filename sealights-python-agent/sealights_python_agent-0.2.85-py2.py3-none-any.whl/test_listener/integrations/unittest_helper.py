import logging.config
import os
import sys
import time

from python_agent.packages.six.moves import reload_module

from python_agent.packages import xmlrunner
from python_agent.test_listener.managers.agent_manager import AgentManager
from python_agent.test_listener.sealights_api import SeaLightsAPI

if os.environ.get("SL_UNITTEST") == "unittest2":
    import unittest2 as unittest
else:
    import unittest

if sys.version_info >= (2, 7):
    loader = unittest.loader.defaultTestLoader
else:
    loader = unittest.defaultTestLoader

__unittest = True

log = logging.getLogger(__name__)
is_has_tests = True


class SealightsTestResult(unittest.TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        super(SealightsTestResult, self).__init__(stream, descriptions, verbosity)
        self.skipped_tests = {}
        self.error_tests = {}
        self.execution_id = SeaLightsAPI.create_execution_id()

    def startTestRun(self):
        try:
            # startTestRun is called even when there are no tests found. We avoid it here.
            if is_has_tests:
                SeaLightsAPI.notify_execution_start(self.execution_id)
        except Exception as e:
            log.exception("failed sending execution start. error: %s" % str(e))
        super(SealightsTestResult, self).startTestRun()

    def stopTestRun(self):
        try:
            # stopTestRun is called even when there are no tests found. We avoid it here.
            if is_has_tests:
                SeaLightsAPI.notify_execution_end(self.execution_id)
        except Exception as e:
            log.exception("failed sending execution end. error: %s" % str(e))
        super(SealightsTestResult, self).stopTestRun()

    def startTest(self, test):
        try:
            test.start_time = time.time()
            SeaLightsAPI.notify_test_start(self.execution_id, test.id())
        except Exception as e:
            log.exception("failed sending test start. error: %s" % str(e))
        super(SealightsTestResult, self).startTest(test)

    def stopTest(self, test):
        try:
            if not self.skipped_tests.get(test.id()) and not self.error_tests.get(test.id()):
                test.end_time = time.time()
                test.duration = test.end_time - test.start_time
                SeaLightsAPI.notify_test_end(self.execution_id, test.id(), test.duration, "passed")
        except Exception as e:
            log.exception("failed sending test end. error: %s" % str(e))
        super(SealightsTestResult, self).stopTest(test)

    def addError(self, test, err):
        try:
            test.end_time = time.time()
            test.duration = test.end_time - test.start_time
            self.error_tests[test.id()] = test.id()
            SeaLightsAPI.notify_test_end(self.execution_id, test.id(), test.duration, "failed")
        except Exception as e:
            log.exception("failed sending test failed. error: %s" % str(e))
        super(SealightsTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        try:
            test.end_time = time.time()
            test.duration = test.end_time - test.start_time
            self.error_tests[test.id()] = test.id()
            SeaLightsAPI.notify_test_end(self.execution_id, test.id(), test.duration, "failed")
        except Exception as e:
            log.exception("failed sending test failed. error: %s" % str(e))
        super(SealightsTestResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        try:
            test.end_time = time.time()
            test.duration = test.end_time - test.start_time
            self.skipped_tests[test.id()] = test.id()
            SeaLightsAPI.notify_test_end(self.execution_id, test.id(), test.duration, "skipped")
        except Exception as e:
            log.exception("failed sending test skipped. error: %s" % str(e))
        super(SealightsTestResult, self).addSkip(test, reason)


class SealightsTextTestRunner(unittest.TextTestRunner):
    resultclass = SealightsTestResult

    def run(self, test):
        if hasattr(test, "_tests") and not test._tests:
            global is_has_tests
            is_has_tests = False
        return super(SealightsTextTestRunner, self).run(test)


class SealightsJunitTestRunner(xmlrunner.XMLTestRunner):
    resultclass = SealightsTestResult

    def run(self, test):
        if hasattr(test, "_tests") and not test._tests:
            global is_has_tests
            is_has_tests = False
        return super(SealightsJunitTestRunner, self).run(test)


class SealightsTestProgram(unittest.TestProgram):

    def __init__(self, module='__main__', defaultTest=None, argv=None,
                 testRunner=None, testLoader=loader,
                 exit=True, verbosity=1, failfast=None, catchbreak=None,
                 buffer=None):

        super(SealightsTestProgram, self).__init__(
            module=module, defaultTest=defaultTest, argv=argv,
            testRunner=testRunner, testLoader=testLoader,
            exit=exit, verbosity=verbosity, failfast=failfast,
            catchbreak=catchbreak, buffer=buffer
        )


def reload_module_based_on_command(args):
    if args and args[0] == "unit2":
        os.environ["SL_UNITTEST"] = "unittest2"
    else:
        os.environ["SL_UNITTEST"] = "unittest"
    reload_module(sys.modules[__name__])


def main(args, is_junit=False, output="."):
    try:
        reload_module_based_on_command(args)
        SealightsTestProgram.USAGE = getattr(unittest, "USAGE_AS_MAIN", "")
        runner = SealightsTextTestRunner()
        if is_junit:
            runner = SealightsJunitTestRunner(output=output)
        SealightsTestProgram(module=None, testRunner=runner, argv=args, exit=False)
    except SystemExit as e:
        log.exception("Failed Running Unittests With Args: %s. Error: %s" % (args, str(e)))
    except Exception as e:
        log.exception("Failed Running Unittests With Args: %s. Error: %s" % (args, str(e)))

