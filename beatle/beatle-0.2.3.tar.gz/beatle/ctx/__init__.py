# -*- coding: utf-8 -*-


from context import context
from context import localcontext
from logger import logger


if 'THE_CONTEXT' not in globals():
    THE_CONTEXT = localcontext()
