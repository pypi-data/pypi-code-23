from concurrent.futures import ThreadPoolExecutor
from functools import partial

import trio
from sqlalchemy.engine import Engine
from sqlalchemy.engine.strategies import DefaultEngineStrategy

from .engine import AsyncioEngine


TRIO_STRATEGY = '_trio'


async def _run_in_thread(_func, *args, **kwargs):
    # use _executor and _func in case we're called with kwargs
    # "executor" or "func".
    if kwargs:
        _func = partial(_func, **kwargs)

    return await trio.run_in_worker_thread(_func, *args)


class TrioEngine(AsyncioEngine):
    def __init__(self, pool, dialect, url, logging_name=None, echo=None,
                 execution_options=None, **kwargs):

        self._engine = Engine(
            pool, dialect, url, logging_name=logging_name, echo=echo,
            execution_options=execution_options, **kwargs)

        max_workers = None

        # https://www.python.org/dev/peps/pep-0249/#threadsafety
        if dialect.dbapi.threadsafety < 2:
            # This might seem overly-restrictive, but when we instantiate an
            # AsyncioResultProxy from AsyncioEngine.execute, subsequent
            # fetchone calls could be in different threads. Let's limit to one.
            max_workers = 1

        self._engine_executor = ThreadPoolExecutor(max_workers=max_workers)

    async def _run_in_thread(_self, _func, *args, **kwargs):
        return await _run_in_thread(_func, *args, **kwargs)


class TrioEngineStrategy(DefaultEngineStrategy):
    name = TRIO_STRATEGY
    engine_cls = TrioEngine

TrioEngineStrategy()
