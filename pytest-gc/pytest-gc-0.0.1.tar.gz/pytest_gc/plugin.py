import functools
import gc
import os

import pytest
import six

default_scope = six.get_function_defaults(pytest.fixture)[0]
scope = os.environ.get('gc_scope', default_scope)


@pytest.fixture(scope, autouse=True)
def switch(request):
    if request.config.getoption('gc_disable'):
        request.addfinalizer(gc.enable)
        gc.disable()


@pytest.fixture(scope, autouse=True)
def change_threshold(request):
    threshold = request.config.getoption('gc_threshold')
    if threshold:
        request.addfinalizer(
            functools.partial(gc.set_threshold, *gc.get_threshold())
        )
        gc.set_threshold(*threshold)
