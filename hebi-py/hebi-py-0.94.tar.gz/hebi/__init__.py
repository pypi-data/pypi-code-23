# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Core python API

This holds the bindings for the HEBI Core API. The binary must be present on
your system.

Note: C Library will be searched using ctypes. If you would like to force a
certain shared library to be loaded, set the HEBI_C_LIB environment variable
to the location of the binary.
"""


# -----------------------------------------------------------------------------
# Lookup API
# -----------------------------------------------------------------------------


class Lookup(object):
  """
  Maintains a registry of network-connected modules
  and returns Group objects to the user.
  """

  DEFAULT_TIMEOUT_MS = 500

  def __init__(self):
    from ._internal import lookup
    self.__delegate = lookup.LookupDelegate()

  @property
  def entrylist(self):
    """
    A list of discovered network connected modules.
    """
    return self.__delegate.entrylist

  def get_group_from_names(self, families, names, timeout_ms=None):
    """
    Get a group from modules with the given names and families.

    If the families or names provided as input is only a single element,
    then that element is assumed to pair with each item in the other parameter.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after ``DEFAULT_TIMEOUT_MS`` milliseconds,
    if a matching group cannot be constructed.

    :param families:
    :param names:
    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       Lookup.DEFAULT_TIMEOUT_MS.

    :return:
    """
    return self.__delegate.get_group_from_names(families, names, timeout_ms)

  def get_group_from_macs(self, addresses, timeout_ms=None):
    """
    Get a group from modules with the given mac addresses.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after ``DEFAULT_TIMEOUT_MS`` milliseconds,
    if a matching group cannot be constructed.

    :param addresses:
    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       Lookup.DEFAULT_TIMEOUT_MS.

    :return:
    """
    return self.__delegate.get_group_from_macs(addresses, timeout_ms)

  def get_group_from_family(self, family, timeout_ms=None):
    """
    Get a group from all known modules with the given family.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after ``DEFAULT_TIMEOUT_MS`` milliseconds,
    if a matching group cannot be constructed.

    :param family:
    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       Lookup.DEFAULT_TIMEOUT_MS.

    :return:
    """
    return self.__delegate.get_group_from_family(family, timeout_ms)

  def get_connected_group_from_name(self, family, name, timeout_ms=None):
    """
    Get a group from all modules known to connect to a module with
    the given name and family.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after ``DEFAULT_TIMEOUT_MS`` milliseconds,
    if a matching group cannot be constructed.

    :param family:
    :param name:
    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       Lookup.DEFAULT_TIMEOUT_MS.

    :return:
    """
    return self.__delegate.get_connected_group_from_name(family, name, timeout_ms)

  def get_connected_group_from_mac(self, address, timeout_ms=None):
    """
    Get a group from all modules known to connect to a module with
    the given mac address.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after ``DEFAULT_TIMEOUT_MS`` milliseconds,
    if a matching group cannot be constructed.

    :param address:
    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       Lookup.DEFAULT_TIMEOUT_MS.

    :return:
    """
    return self.__delegate.get_connected_group_from_mac(address, timeout_ms)


# -----------------------------------------------------------------------------
# Message Types
# -----------------------------------------------------------------------------

from ._internal.messages import GroupCommand, GroupFeedback, GroupInfo
from ._internal.graphics import Color
from . import robot_model, trajectory, util