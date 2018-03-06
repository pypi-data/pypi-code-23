from multiprocessing import Process, cpu_count
__all__ = ["UnorderedQMap"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.1.0"


SENTINEL = "StOp The W0rld"


def worker(inQ, outQ):
  for func, args, kwargs in iter(inQ.get, SENTINEL):
    outQ.put(func(*args, **kwargs))


class UnorderedQMap(object):
  """Maps input Queue of 3-tuples: (function, (*args), {**kwargs})
  onto Queue of results with Context Manager syntax
  Example Usage:

  >>> from multiprocessing import Queue
  >>> def stringify(*a, **k):
  ...   return str((a, k))
  ...
  >>> inQ, outQ = Queue(), Queue()
  >>> for i in range(10):
  ...   inQ.put((stringify, (i, "say"), dict(hello="world"[i % 5])))
  ...
  >>> with UnorderedQMap(outQ, inQ):
  ...   for i in range(10):
  ...     print(outQ.get())
  """
  try:
    CPU_COUNT = cpu_count()
  except Exception:  # pragma: no cover
    CPU_COUNT = 4

  def __init__(self, resultQ, inputQ, processes=None):
    """Careful to put results Q first.
    `max_processes` default: cpu_count()
    """
    self.iQ = inputQ
    self.oQ = resultQ
    self.n = self.CPU_COUNT if processes is None else processes

  def __enter__(self):
    # Start worker processes
    for i in range(self.n):
      Process(target=worker, args=(self.iQ, self.oQ)).start()

  def __exit__(self, *exc):
    for i in range(self.n):
      self.iQ.put(SENTINEL)
    return False
