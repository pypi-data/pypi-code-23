# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals


import tcell_agent
from tcell_agent.agent import TCellAgent
from tcell_agent.tcell_logger import get_module_logger

_started = False


def instrument_gunicorn():
    from gunicorn.arbiter import Arbiter
    old_func = Arbiter.start

    def start(self):
        if tcell_agent.instrumentation.gunicorn_tcell._started is False:
            get_module_logger(__name__).info("Staring (gunicorn) agent")
            tcell_agent.instrumentation.gunicorn_tcell._started = True
            TCellAgent.get_agent().ensure_polling_thread_running()
        return old_func(self)

    Arbiter.start = start


try:
    instrument_gunicorn()
except ImportError as ie:
    pass
except Exception as e:
    get_module_logger(__name__).debug("Could not instrument gunicorn: {e}".format(e=e))
    get_module_logger(__name__).debug(e, exc_info=True)
