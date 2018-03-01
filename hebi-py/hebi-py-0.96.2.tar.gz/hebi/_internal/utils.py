# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Internal Utilities API

This is an internal API. You should not use this code directly.
"""


import weakref


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class WeakReferenceContainer(object):
  """
  Small wrapper around a weak reference. For internal use - do not use directly.
  """

  def _get_ref(self):
    ref = self._weak_ref()
    if (ref):
      return ref
    raise RuntimeError('Reference no longer valid due to finalization')

  def __init__(self, ref):
    self._weak_ref = weakref.ref(ref)


class AtomicCounter(object):
  """
  An atomic counter implementation. For internal use - do not use directly.
  """

  def __init__(self):
    import threading
    self._lock = threading.Lock()
    self._counter = 1

  def decrement(self):
    with self._lock:
      self._counter = self._counter - 1

  def increment(self):
    with self._lock:
      self._counter = self._counter + 1

  @property
  def count(self):
    with self._lock:
      return self._counter

