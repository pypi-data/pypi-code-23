# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Log File API
-----------------
"""

from ctypes import c_size_t, c_char_p, byref
import numpy as np

from .messages import GroupFeedback
from .raw import (hebiLogFileGetNumberOfModules, hebiLogFileRelease,
                  hebiLogFileGetFileName, hebiLogFileGetNextFeedback,
                  StatusSuccess, UnmanagedObject)

from .type_utils import decode_string_buffer as decode_str
from .type_utils import create_string_buffer_compat as create_str

class LogFileDelegate(UnmanagedObject):
  """
  Represents a file which contains previously recorded group messages.
  """

  __micro_to_seconds = 0.000001

  def __calculate_time(self):
    # Revisit: Don't use hwTx and use pcRx like MATLAB does
    rx_time = self._next_feedback.hardware_transmit_time
    np.subtract(rx_time, self._beginning_time, rx_time)
    np.multiply(rx_time, LogFileDelegate.__micro_to_seconds, self._time)

  def __read_first_feedback(self):
    feedback = GroupFeedback(self._number_of_modules)
    if (hebiLogFileGetNextFeedback(self, feedback) != StatusSuccess):
      raise RuntimeError('Log file is corrupt or has no feedback')

    self._next_feedback = feedback
    # Revisit: Don't use hwTx and use pcRx like MATLAB does
    start_time = self._next_feedback.hardware_transmit_time.min()

    # Cached arrays
    self._beginning_time = np.array([start_time] * self._number_of_modules,
                                     np.uint64)
    self._time = np.empty(self._number_of_modules, np.float64)
    self.__calculate_time()


  def __init__(self, internal):
    """
    This is invoked internally. Do not use directly.
    """
    super(LogFileDelegate, self).__init__(internal, on_delete=hebiLogFileRelease)
    self._feedbacks_read = 0
    self._number_of_modules = hebiLogFileGetNumberOfModules(internal)
    if (self._number_of_modules < 1):
      raise RuntimeError('Log file is corrupt')

    self.__read_first_feedback()

  @property
  def filename(self):
    """
    The file name of the log file.
    """
    str_len = c_size_t(0)
    if (hebiLogFileGetFileName(self, c_char_p(None), byref(str_len))
      != StatusSuccess):
      return None

    str_buffer = create_str(str_len.value)

    if (hebiLogFileGetFileName(self, str_buffer, byref(str_len)) != StatusSuccess):
      return None

    return decode_str(str_buffer.value)

  @property
  def number_of_modules(self):
    """
    The number of modules in the group.
    """
    return self._number_of_modules

  def get_next_feedback(self, reuse_fbk=None):
    """
    Retrieves the next group feedback from the log file, if any exists.
    This function acts as a forward sequential iterator over the data
    in the file. Each subsequent call to this function moves farther
    into the file. When the end of the file is reached, all subsequent calls
    to this function returns ``None``

    **Warning:** any preexisting data in the provided Feedback object is erased.

    :param reuse_fbk: An optional parameter which can be used to reuse
                      an existing *GroupFeedback* instance. It is recommended
                      to provide this parameter inside a repetitive loop,
                      as reusing feedback instances results in substantially
                      fewer heap allocations.

    :return: The most recent feedback, provided one is available.
             ``None`` is returned if there is no available feedback.
    """
    if (self._next_feedback == None):
      return None

    ret = TimedGroupFeedback(self._next_feedback, self._time.copy())

    # FIXME: when C API has a `copy one group feedback into another` feature,
    # change to that. Because we don't need to be allocating more GroupFeedbacks
    # instead, like this.
    self._next_feedback = GroupFeedback(ret.size)
    if (hebiLogFileGetNextFeedback(self, self._next_feedback) != StatusSuccess):
      self._next_feedback = None
    else:
      self.__calculate_time()

    self._feedbacks_read = self._feedbacks_read + 1
    return ret


class TimedGroupFeedback(GroupFeedback):

  def __init__(self, group_feedback, time):
    super(TimedGroupFeedback, self).__init__(group_feedback.size, group_feedback)
    self._time = time

  @property
  def time(self):
    return self._time.copy()


# For now, these are the same
LogFile = LogFileDelegate