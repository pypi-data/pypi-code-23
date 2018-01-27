import importlib
from io import StringIO
import unittest

import pytest


CRICRI_BASES = []


class CricriException(Exception):
    """
    Raised when cricri failed
    """


class CricriItem(pytest.Item):

    def __init__(self, name, parent, test_case):
        super(CricriItem, self).__init__(name, parent)
        self.cricri_output = StringIO()
        self.test_case = test_case

    def runtest(self):
        unittest_loader = unittest.TestLoader()
        test_runner = unittest.TextTestRunner(self.cricri_output, verbosity=2)
        result = test_runner.run(
            unittest_loader.loadTestsFromTestCase(
                self.test_case))
        if result.failures:
            raise CricriException(result)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, CricriException):
            return self.cricri_output.getvalue()

    def reportinfo(self):
        return self.fspath, 0, "scenario: {}".format(self.name)


def pytest_addoption(parser):
    """Add options to mount cricri base test class"""

    group = parser.getgroup('cricri', 'cricri')
    group.addoption('--cricri-base', action='append', default=[], metavar='BASE CLASS',
                    dest='cricri_bases',
                    help='package.module.BaseClass or package.module.BaseClass:max_loop')


def pytest_configure(config):
    CRICRI_BASES.extend(config.getvalue('cricri_bases'))


def pytest_collection_modifyitems(session, items):
    for cricri_base in CRICRI_BASES:
        module, base_cls_name = cricri_base.rsplit('.', 1)
        if ':' in base_cls_name:
            base_cls_name, max_loop = base_cls_name.split(':', 1)
            max_loop = int(max_loop)
        else:
            max_loop = 2

        module_obj = importlib.import_module(module)
        base_cls = getattr(module_obj, base_cls_name)

        for test_case in base_cls.get_test_cases(max_loop):
            item = CricriItem(test_case.__name__, session, test_case)
            items.append(item)
