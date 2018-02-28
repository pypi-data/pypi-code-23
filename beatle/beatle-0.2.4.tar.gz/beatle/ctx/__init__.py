# -*- coding: utf-8 -*-


from ._context import context
from ._context import localcontext
from ._logger import logger


if 'THE_CONTEXT' not in globals():
    THE_CONTEXT = localcontext()

def get_context():
    global THE_CONTEXT
    return THE_CONTEXT