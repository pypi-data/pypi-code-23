# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Utilities API
------------------
"""


def create_imitation_group(size):
  """
  Create an imitation group of the provided size.

  If size is less than 1, a ValueError will be thrown.

  :param size: The number of modules in the imitation group. Must be an ``int``
  :return: a Group instance. This will never be ``None``
  """
  from ._internal.group import create_imitation_group as create
  return create(size)

def load_log(file):
  """
  Opens an existing log file.

  :param file:
  :return:
  """
  from os.path import isfile
  if (file == None):
    raise ValueError('file location cannot be null')
  elif not (isfile(file)):
    raise RuntimeError('file {0} does not exist'.format(file))

  from ._internal.raw import hebiLogFileOpen
  from ._internal.log_file import LogFile

  log_file = hebiLogFileOpen(file.encode('utf-8'))
  if (log_file == None):
    raise RuntimeError('file {0} is not a valid log file'.format(file))

  return LogFile(log_file)


def plot_logs(logs, feedbackField, modules):
  """
  TODO: Document and Implement
  """

  from ._internal.log_file import LogFile
  if (isinstance(logs, LogFile)):
    logs = [ logs ] # Convert 1 log to list

  raise NotImplementedError()


def plot_trajectory(trajectory, dt=0.01):
  """
  TODO: Document and Implement
  """

  raise NotImplementedError()

