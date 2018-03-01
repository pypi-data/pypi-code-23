# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Internal Group API

This is an internal API. You should not use this code directly.
"""

from ctypes import CFUNCTYPE, c_size_t, c_void_p, c_char_p, byref

from .log_file import LogFile
from .messages import GroupFeedback, GroupInfo
from .raw import *
from . import type_utils

class Group(object):
  """
  Represents a group of physical HEBI modules, and allows Command,
  Feedback, and Info objects to be sent to and recieved from the hardware.
  """

  DEFAULT_TIMEOUT_MS = 500
  """
  The default timeout (in milliseconds)
  """

  def __init__(self, delegate):
    """
    This is created internally. Do not instantiate directly.
    """
    self.__delegate = delegate

  @property
  def size(self):
    """
    The number of modules in the group.

    :return: size of the group
    :rtype:  int
    """
    return self.__delegate.size

  @property
  def feedback_frequency(self):
    """
    The frequency of the internal feedback request + callback thread.

    :return: the frequency
    :rtype:  float
    """
    return self.__delegate.feedback_frequency

  @feedback_frequency.setter
  def feedback_frequency(self, value):
    """
    Sets the frequency of the internal feedback request + callback thread.

    :param value: the new frequency, in hertz
    :type value:  float
    """
    self.__delegate.feedback_frequency = value

  @property
  def command_lifetime(self):
    """
    The command lifetime for the modules in this group.

    :return: the command lifetime
    :rtype:  int
    """
    return self.__delegate.command_lifetime

  @command_lifetime.setter
  def command_lifetime(self, value):
    """
    Set the command lifetime for the modules in this group.

    This parameter defines how long a module will execute a command set
    point sent to it. Note the commands from other systems/applications
    are ignored during this time. A value of ``0`` indicates commands last
    forever, and there is no lockout behavior.

    :param value: The command lifetime, in milliseconds
    :type value:  int
    """
    self.__delegate.command_lifetime = value

  def send_command(self, group_command):
    """
    Send a command to the given group without requesting an acknowledgement.
    This is appropriate for high-frequency applications.

    :param group_command: The command to send
    :type group_command:  GroupCommand

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_command(group_command)

  def send_command_with_acknowledgement(self, group_command, timeout_ms=None):
    """
    Send a command to the given group, requesting an acknowledgement
    of transmission to be sent back.

    Note: A non-true return does not indicate a specific failure, and may
    result from an error while sending or simply a timeout/dropped response
    packet after a successful transmission.

    :param group_command: The command to send
    :type group_command:  GroupCommand

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_command_with_acknowledgement(group_command,
                                                             timeout_ms)

  def send_feedback_request(self):
    """
    Requests feedback from the group.

    Sends a background request to the modules in the group; if/when all modules
    return feedback, any associated handler functions are called. This returned
    feedback is also stored to be returned by the next call to
    :meth:`.get_next_feedback` (any previously returned data is discarded).
    
    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_feedback_request()

  def get_next_feedback(self, timeout_ms=None, reuse_fbk=None):
    """
    Returns the most recently stored feedback from a sent feedback request, or
    the next one received (up to the requested timeout).

    Note that a feedback request can be sent either with the
    send_feedback_request function, or by setting a background feedback
    frequency with :attr:`.feedback_frequency`.

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :param reuse_fbk: An optional parameter which can be used to reuse
                      an existing GroupFeedback instance. It is recommended
                      to provide this parameter inside a repetitive loop,
                      as reusing feedback instances results in substantially
                      fewer heap allocations.
    :type reuse_fbk:  GroupFeedback

    :return: The most recent feedback, provided one became available before the
             timeout. ``None`` is returned if there was no available feedback.
    :rtype:  GroupFeedback
    """
    return self.__delegate.get_next_feedback(timeout_ms, reuse_fbk)

  def request_info(self, timeout_ms=None, reuse_info=None):
    """
    Request info from the group, and store it in the passed-in info object.

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :param reuse_info: An optional parameter which can be used to reuse
                       an existing GroupInfo instance. It is recommended
                       to provide this parameter inside a repetitive loop,
                       as reusing info instances results in substantially
                       fewer heap allocations.
    :type reuse_info:  GroupInfo

    :return: the updated info on success, ``None`` otherwise
    :rtype:  GroupInfo
    """
    return self.__delegate.request_info(timeout_ms, reuse_info)

  def start_log(self, directory=None, name=None):
    """
    Start logging information and feedback from this group.
    If a log file was already started before this (and not stopped using stop_log),
    then that file will automatically be gracefully closed.

    :param directory: Optional directory into which the log file will be created.
                      If ``None``, the process' current working directory is used.
    :type directory:  str

    :param name: Optional name of the log file.
                 If ``None``, a name will be generated using the time
                 at which this function was invoked.
    :type name:  str

    :return: The path, including the file, of the log file
             or ``None`` on failure
    :rtype:  str
    """
    return self.__delegate.start_log(directory, name)

  def stop_log(self):
    """
    Stop logging data into the last opened log file.
    If no log file was opened, None will be returned.
    If an error occurs while stopping the previously started
    log file, None will be returned.

    :return: a LogFile object on success, or None
    :rtype:  LogFile
    """
    return self.__delegate.stop_log()

  def add_feedback_handler(self, handler):
    """
    Adds a handler function to be called by the internal feedback request thread.

    Note that this function must execute very quickly:
    If a handler takes more time than the reciprocal of the feedback
    thread frequency, the thread will saturate in feedback events to dispatch.
    This may cause feedback packets to be dropped from handler dispatch,
    or delayed invocation of the feedback handlers.

    :param handler: A function which is able to accept a single argument
    """
    self.__delegate.add_feedback_handler(handler)

  def clear_feedback_handlers(self):
    """
    Removes all feedback handlers presently added.
    """
    self.__delegate.clear_feedback_handlers()


class GroupDelegate(UnmanagedObject):
  """
  Delegate for Group
  """

  def __parse_to(self, timeout_ms):
    if (timeout_ms == None):
      return Group.DEFAULT_TIMEOUT_MS
    else:
      try:
        return int(timeout_ms)
      except:
        raise ValueError('timeout_ms must be a number')

  def __feedback_handler(self, c_fbk, c_data):

    from .messages import SharedGroupMessage
    class FakeRefCountedSharedHandle(SharedGroupMessage):
      """
      Use this to fake super class into thinking we're actually caring about
      tracking ownership of an object that we don't manage or own
      """

      def __init__(self, number_of_modules, internal):
        def passthrough(number_of_modules):
          return internal
        super(FakeRefCountedSharedHandle, self).__init__(number_of_modules,
                                                         passthrough, None)

    class FlyweightGroupFeedback(GroupFeedback):

      def __del__(self):
        # No-Op
        pass

      def __init__(self, number_of_modules, internal):
        self._internal = internal
        self._ref = FakeRefCountedSharedHandle(number_of_modules, internal)
        self._number_of_modules = number_of_modules
        super(FlyweightGroupFeedback, self).__init__(number_of_modules, self)
        self._ref._refcount.decrement() # Decrement since we added self as an owner


    feedback = FlyweightGroupFeedback(self._number_of_modules, c_fbk)
    for entry in self._feedback_callbacks:
      entry(feedback)

  def __setup_feedback_handler(self):
    fbk_handler = self.__feedback_handler
    c_callback_t = CFUNCTYPE(None, c_void_p, c_void_p)
    c_callback = c_callback_t(fbk_handler)
    self._c_callback = c_callback
    hebiGroupRegisterFeedbackHandler(self, c_callback, c_void_p(0))

  def __init__(self, internal):
    super(GroupDelegate, self).__init__(internal, on_delete=hebiGroupRelease)
    self._number_of_modules = int(hebiGroupGetSize(internal))
    self._feedback_callbacks = list()
    # Set up handler to pass to C API
    self.__setup_feedback_handler()

  @property
  def size(self):
    return self._number_of_modules

  @property
  def feedback_frequency(self):
    return float(hebiGroupGetFeedbackFrequencyHz(self))

  @feedback_frequency.setter
  def feedback_frequency(self, value):
    try:
      value = float(value)
    except:
      raise ValueError("frequency must be a number")
    if (hebiGroupSetFeedbackFrequencyHz(self, value) != StatusSuccess):
      raise RuntimeError('Could not set feedback frequency')

  @property
  def command_lifetime(self):
    return int(hebiGroupGetCommandLifetime(self))

  @command_lifetime.setter
  def command_lifetime(self, value):
    try:
      value = int(value)
    except:
      raise ValueError("lifetime must be a number")
    if(hebiGroupSetCommandLifetime(self, value) != StatusSuccess):
      raise RuntimeError('Could not set command lifetime')

  def send_command(self, group_command):
    return hebiGroupSendCommand(self, group_command) == StatusSuccess

  def send_command_with_acknowledgement(self, group_command, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    return (
      hebiGroupSendCommandWithAcknowledgement(self, group_command, timeout_ms)
      == StatusSuccess)

  def send_feedback_request(self):
    return (hebiGroupSendFeedbackRequest(self) == StatusSuccess)

  def get_next_feedback(self, timeout_ms=None, reuse_fbk=None):
    timeout_ms = self.__parse_to(timeout_ms)
    if (reuse_fbk):
      feedback = GroupFeedback(self._number_of_modules, reuse_fbk)
    else:
      feedback = GroupFeedback(self._number_of_modules)

    res = hebiGroupGetNextFeedback(self, feedback, timeout_ms)
    if (res == StatusSuccess):
      return feedback
    else:
      return None

  def request_info(self, timeout_ms=None, reuse_info=None):
    timeout_ms = self.__parse_to(timeout_ms)
    if (reuse_info):
      info = GroupInfo(self._number_of_modules)
    else:
      info = GroupInfo(self._number_of_modules, reuse_info)

    res = hebiGroupRequestInfo(self, info, timeout_ms)
    if (res == StatusSuccess):
      return info
    else:
      return None

  def start_log(self, directory=None, name=None):
    from .type_utils import create_string_buffer_compat as str_buffer

    if (directory):
      directory = str(directory)
      c_directory = str_buffer(directory, len(directory))
    else:
      c_directory = c_char_p(None)

    if (name):
      name = str(name)
      c_name = str_buffer(name, len(name))
    else:
      c_name = c_char_p(None)

    c_string_ret = c_void_p(0)
    res = hebiGroupStartLog(self, c_directory, c_name, byref(c_string_ret))

    if (res == StatusSuccess):
      c_str_length = c_size_t(0)
      hebiStringGetString(c_string_ret, c_char_p(None), byref(c_str_length))

      if (c_str_length.value == 0): # Unknown error
        hebiStringRelease(c_string_ret)
        raise RuntimeError(
          'Underlying C API call hebiStringGetString'
          'returned length of zero')

      c_str_buffer = str_buffer(c_str_length.value)
      hebiStringGetString(c_string_ret, c_str_buffer, byref(c_str_length))

      ret = c_str_buffer.value.decode('utf-8')
      hebiStringRelease(c_string_ret)
      return ret

    return None

  def stop_log(self):
    c_log = hebiGroupStopLog(self)
    if (c_log == None):
      return None
    return LogFile(c_log)

  def add_feedback_handler(self, handler):
    if not (handler in self._feedback_callbacks):
      self._feedback_callbacks.append(handler)

  def clear_feedback_handlers(self):
    self._feedback_callbacks = list()


def create_imitation_group(size):
  if (type(size) != int):
    raise TypeError('size must be an int')
  if (size < 1):
    raise ValueError('size must be greater than zero')

  return Group(GroupDelegate(hebiGroupCreateImitation(size)))