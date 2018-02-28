# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------


def create_imitation_group(size):
  """
  Create an imitation group of the provided size.
  The imitation group returned from this function provides the exact same
  interface as a group created from the :class:`Lookup` class.

  However, there are a few subtle differences between the imitation group and
  group returned from a lookup operation. See :ref:`imitation-group-contrast` section
  for more information.

  :param size: The number of modules in the imitation group
  :type size:  int
  
  :return: The imitation group. This will never be ``None``
  :rtype:  Group

  :raises ValueError: If size is less than 1
  """
  from ._internal.group import create_imitation_group as create
  return create(size)


def load_log(file):
  """
  Opens an existing log file.

  :param file: the path to an existing log file
  :type file:  str, unicode

  :return: The log file. This function will never return ``None``
  :rtype:  LogFile
  
  :raises TypeError: If file is an invalid type
  :raises IOError: If the file does not exist or is not a valid log file
  """
  from os.path import isfile
  try:
    f_exists = isfile(file)
  except TypeError as t:
    raise TypeError('Invalid type for file. '
                    'Caught TypeError with message: {0}'.format(t.args))

  if not (f_exists):
    raise IOError('file {0} does not exist'.format(file))

  from ._internal.raw import hebiLogFileOpen
  from ._internal.log_file import LogFile

  log_file = hebiLogFileOpen(file.encode('utf-8'))
  if (log_file == None):
    raise IOError('file {0} is not a valid log file'.format(file))

  return LogFile(log_file)


def plot_logs(logs, fbk_field, modules=None):
  """
  Currently unimplemented. Do not use.

  :param fbk_field: Feedback field to plot
  :type fbk_field:  str, unicode

  :param modules: Optionally select which modules to plot
  :type modules: NoneType, list
  """
  from ._internal.log_file import LogFile
  if (isinstance(logs, LogFile)):
    logs = [ logs ] # Convert 1 log to list

  raise NotImplementedError()


def plot_trajectory(trajectory, dt=0.01):
  """
  Currently unimplemented. Do not use.

  :param trajectory:
  :type trajectory:  Trajectory

  :param dt: Delta between points in trajectory to plot
  :type dt:  int, float
  """
  raise NotImplementedError()

