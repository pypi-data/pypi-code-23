# plugin.py
# Copyright (c) 2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

# Standard library imports
from __future__ import print_function
# PyPI imports
import pytest
from _pytest._code.code import ExceptionInfo
from _pytest.outcomes import skip
from _pytest.runner import TestReport
from pmisc.test import _del_pmisc_test_frames


###
# Functions
###
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    This is a copy of the _pytest.runner.pytest_runtest_makereport function
    with only one modification (other than different indentation): the argument
    to the function repr_failure is filtered by the _del_pmisc_test_frames
    function so that the report given by Pytest stops at the test line that
    generates the exception, not the line within the pmisc.test module that
    actually generates the exception
    """
    # pylint: disable=C0103,R0912,R0914
    when = call.when
    duration = call.stop-call.start
    keywords = dict([(x, 1) for x in item.keywords])
    excinfo = call.excinfo

    sections = []
    if not call.excinfo:
        outcome = "passed"
        longrepr = None
    else:
        if not isinstance(excinfo, ExceptionInfo):
            outcome = "failed"
            longrepr = excinfo
        elif excinfo.errisinstance(skip.Exception):
            outcome = "skipped"
            r = excinfo._getreprcrash()
            longrepr = (str(r.path), r.lineno, r.message)
        else:
            outcome = "failed"
            if call.when == "call":
                longrepr = item.repr_failure(_del_pmisc_test_frames(excinfo))
            else: # exception in setup or teardown
                longrepr = item._repr_failure_py(
                    excinfo, style=item.config.option.tbstyle
                )
    for rwhen, key, content in item._report_sections:
        sections.append(("Captured %s %s" %(key, rwhen), content))
    return TestReport(
        item.nodeid,
        item.location,
        keywords,
        outcome,
        longrepr,
        when,
        sections,
        duration
    )
