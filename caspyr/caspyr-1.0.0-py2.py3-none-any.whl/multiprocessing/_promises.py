r"""
>>> import sys
>>> from time import time, sleep
>>>
>>> def prnt(*a):
...   pass  # sys.stderr.write(' '.join(map(str, a)))
...
>>> def stringify(*a):
...   sleep(0.1)
...   return str(a)
...
>>> inQ = []
>>> for i in range(10):
...   inQ.append(((i, "say"), dict(hello="world"[i % 5])))
...
>>> tic1 = time()
>>> res1 = promise_map(stringify, inQ)
>>>
>>> # should increase "new" time by 0.2s
>>> prnt(8, res1[8])
>>> prnt(8, res1[8])
>>> prnt(8, res1[8])
>>> prnt(7, res1[7])
>>>
>>> # old version ("new" should finish during this time)
>>> tic2 = time()
>>> res2 = map(stringify, inQ)
>>> tic2 = time() - tic2
>>>
>>> # should not increase "new" time
>>> prnt(9, res1[9])
>>>
>>> sys.stderr.write("old: %.3gs\n" % tic2)
>>> for i in range(len(res1)):
...   prnt(i, res1[i])
...
>>> tic1 = time() - tic1
>>> sys.stderr.write("new: %.3gs\n" % (tic1 - tic2))
"""
from threading import Thread
from time import time
import logging
from ._multiprocessing import cpu_count
from tqdm import tqdm


__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.1.0"


class Mapper(object):
  @classmethod
  def map(cls, func, seq, **k):
    """Non-blocking concurrent version of map(func, seq).

    Returns a list-like object which if necessary blocks and
    forces calculation upon individual element access.
    """
    return cls([(func, a, {}) for a in seq], **k)

  def __getitem__(self, i):
    raise NotImplementedError

  def __len__(self):
    raise NotImplementedError

  def __iter__(self):
    for i in range(len(self)):
      yield self[i]
    raise StopIteration
    return

  def __reversed__(self):
    for i in reversed(range(len(self))):
      yield self[i]
    raise StopIteration
    return


class PromiseMap(Thread, Mapper):
  def __init__(self, func_args_kwargs, nostart=False):
    """func_args_kwargs  : 3-tuple, (func, (*args), {**kwargs})"""
    Thread.__init__(self)
    self.daemon = True  # kill thread when main killed (KeyboardInterrupt)
    self.was_killed = False
    self._fak = func_args_kwargs
    self._results = [None] * len(func_args_kwargs)
    self.started = time()
    if not nostart:
      self.start()

  def exit(self):
    self.was_killed = True
    # self.join()  # DO NOT, blocking event, slows down at closing
    return self.report()

  def run(self):
    log = logging.getLogger(__name__)
    for i in range(len(self)):
      # Quit if killed
      # if self.exit_event.is_set():  # TODO: should work but does not...
      if self.was_killed:
        self.was_killed = time() - self.started
        return
      self[i]
    self.was_killed = time() - self.started
    log.info("delivered:" + tqdm.format_interval(self.was_killed))

  def report(self):
    # return self.is_alive()  # TODO: does not work...
    return not self.was_killed

  def __getitem__(self, i):
    if isinstance(i, slice):
      return [self[j] for j in range(len(self))[i]]
    if self._results[i] is None:
      self._results[i] = self._fak[i][0](*self._fak[i][1], **self._fak[i][2])
    return self._results[i]

  def __len__(self):
    return len(self._fak)


promise_map = PromiseMap.map


class PromiseMultiMap(Mapper):
  def __init__(self, func_args_kwargs, nthreads=None, **k):
    """nthreads  : int, (default: caspyr.multiprocessing.cpu_count())"""
    nthreads = nthreads or cpu_count()
    self._threads = [PromiseMap(func_args_kwargs[i::nthreads], **k)
                     for i in range(nthreads)]

  def __getitem__(self, i):
    if isinstance(i, slice):
      return [self[j] for j in range(len(self))[i]]
    j, tid = divmod(i, len(self._threads))
    return self._threads[tid][j]

  def __len__(self):
    return sum(map(len, self._threads))


promise_mmap = PromiseMultiMap.map
