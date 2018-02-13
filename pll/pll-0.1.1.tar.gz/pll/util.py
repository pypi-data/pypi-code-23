from typing import Callable, Any, Iterable, Awaitable, TypeVar

import asyncio
from functools import wraps

import tqdm  # type: ignore

from .fmap import fmap  # NOQA


A = TypeVar('A')


def as_submitted(it : Iterable[Awaitable[A]]
                 ) -> Iterable[Awaitable[A]]:
    _ = it
    _ = [asyncio.ensure_future(el) for el in _]

    return _


async def pure(el : A,
               ) -> A:
    return el


def run(coro : Awaitable[A],
        ) -> A:
    return asyncio\
        .get_event_loop()\
        .run_until_complete(coro)


def update_pbar(f    : Callable,
                pbar : tqdm.tqdm,
                n    : int = 1,
                ) -> Callable:
    @wraps(f)
    def _update_pbar(*args    : Any,
                     **kwargs : Any,
                     ) -> Any:
        result = f(*args, **kwargs)
        pbar.update(n)
        return result

    return _update_pbar
