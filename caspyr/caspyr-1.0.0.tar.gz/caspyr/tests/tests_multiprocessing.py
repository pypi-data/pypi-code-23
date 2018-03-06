from __future__ import print_function
from caspyr.multiprocessing import UnorderedQMap, Queue, Manager, \
    freeze_support
from time import sleep
from random import random


def stringify(*a, **k):
  return str((a, k))


def dummyFunc(resVec, i, resLen, **kwargs):
  assert i < resLen
  sleep(random() / 10)
  resVec[i] = "index %d says %s" % (i, str(kwargs))
  return i


def test_basic():
  """Test shortest canonical example"""
  inQ, outQ = Queue(), Queue()
  for i in range(10):
    inQ.put((stringify, (i, "say"), dict(hello="world"[i % 5])))

  with UnorderedQMap(outQ, inQ):
    for i in range(10):
      print(outQ.get())


def test_basic2():
  """Test managed list task despatch"""
  NUM_TASKS = 20

  # Create queues
  taskQ = Queue()
  resIdxQ = Queue()
  manager = Manager()
  results = manager.list([None] * NUM_TASKS)

  # Submit tasks
  [taskQ.put((dummyFunc, (results, i, NUM_TASKS), {"what": i % 2}))
   for i in range(NUM_TASKS)]

  # Start worker processes
  with UnorderedQMap(resIdxQ, taskQ):
    # Get and print results
    print("Unordered results:")
    for _ in range(NUM_TASKS):
      print(results[resIdxQ.get()])


if __name__ == "__main__":
  freeze_support()
  test_basic()
  test_basic2()
