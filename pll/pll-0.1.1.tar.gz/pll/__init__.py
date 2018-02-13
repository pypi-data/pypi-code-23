from typing import (
    Generic, TypeVar, Iterable, Iterator,
    Awaitable, Callable, Any, List, Optional
)
from asyncio import AbstractEventLoop
from concurrent.futures import Executor

import asyncio
from functools import reduce

import tqdm  # type: ignore

from .util import as_submitted, pure, run, fmap, update_pbar


A = TypeVar('A')
B = TypeVar('B')


class Pll(Generic[A], Iterable[A]):
    def __init__(self,
                 it : Iterable[Awaitable[A]],
                 *,
                 executor : Executor = None,
                 pbars : List[tqdm.tqdm] = [],
                 ) -> None:
        self.it = it
        self.executor = executor
        self.pbars = pbars

    @classmethod
    def from_non_coroutines(cls,
                            it : Iterable[A],
                            ) -> 'Pll[A]':
        return cls(as_submitted(pure(el) for el in it))

    def __reconstruct(self,
                      it : Iterable[Awaitable[B]],
                      executor : Executor = None,
                      pbars : List[tqdm.tqdm] = None,
                      ) -> 'Pll[B]':
        if executor is None:
            executor = self.executor
        if pbars is None:
            pbars = self.pbars

        return Pll(it,
                   executor=executor,
                   pbars=pbars,
                   )

    def __iter__(self,
                 ) -> Iterator[A]:
        try:
            for el in self.it:
                yield run(el)
        finally:
            for pbar in self.pbars:
                pbar.close()

    def map(self,
            f : Callable[[A], B],
            ) -> 'Pll[B]':
        _ : Any
        _ = self.it
        _ = fmap(fmap(f), _)

        return self.__reconstruct(_)

    def map_in_executor(self,
                        f : Callable[[A], B],
                        executor : Executor = None,
                        loop : AbstractEventLoop = None,
                        ) -> 'Pll[B]':
        if executor is None:
            executor = self.executor
        if loop is None:
            loop = asyncio.get_event_loop()

        async def wrapped(coro : Awaitable[A]) -> B:
            return await loop.run_in_executor(executor, f, await coro)

        _ : Any
        _ = self.it
        _ = fmap(wrapped, _)
        _ = as_submitted(_)

        return self.__reconstruct(_)

    def bind(self,
             f : Callable[[A], Awaitable[B]],
             ) -> 'Pll[B]':
        async def wrapped(coro : Awaitable[A]) -> B:
            return await f(await coro)
        _ : Any
        _ = self.it
        _ = fmap(wrapped, _)
        _ = as_submitted(_)

        return self.__reconstruct(_)

    def show_progress(self,
                      style : Optional[str] = None,
                      ) -> 'Pll[A]':
        if style:
            _tqdm = getattr(tqdm, 'tqdm_' + style)
        else:
            _tqdm = tqdm.tqdm

        _ : Any
        _ = self.it
        _ = list(_)
        pbar = _tqdm(total=len(_))
        _ = fmap(fmap(update_pbar(lambda x: x, pbar)), _)

        return self.__reconstruct(_,
                                  pbars=[*self.pbars, pbar],
                                  )

    def as_completed(self,
                     ) -> 'Pll[A]':
        _ : Any
        _ = self.it
        _ = list(_)
        _ = as_submitted(asyncio.as_completed(_))  # type: ignore

        return self.__reconstruct(_)

    # def accumulate(self,
    #                f :,
    #                ):
    #     ...

    def reduce(self,
               f : Callable[[B, A], B],
               *args : B,
               ) -> B:
        return reduce(f, iter(self), *args)

    def aggregate(self,
                  f : Callable[[Iterable[A]], B],
                  ) -> B:
        return f(iter(self))
