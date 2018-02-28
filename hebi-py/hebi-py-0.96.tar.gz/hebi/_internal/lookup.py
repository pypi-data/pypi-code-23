# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
HEBI Internal Lookup API

This is an internal API. You should not use this code directly.
"""

from ctypes import cast, c_ubyte, c_char_p, c_void_p

from .group import GroupDelegate, Group
from .raw import *
from . import type_utils
from .. import Lookup

from .type_utils import create_string_buffer_compat as create_str
from .type_utils import decode_string_buffer as decode_str

# -----------------------------------------------------------------------------
# Mac Address
# -----------------------------------------------------------------------------


class MacAddress(object):
  """
  A simple wrapper class for internal C-API HebiMacAddress objects to allow
  interfacing with API calls that use MAC addresses.
  """

  def __init__(self, a, b, c, d, e, f):
    self._bytes = (c_ubyte * 6)(*[a, b, c, d, e, f])

  def __str__(self):
    b0 = "%0.2X" % self._bytes[0]
    b1 = "%0.2X" % self._bytes[1]
    b2 = "%0.2X" % self._bytes[2]
    b3 = "%0.2X" % self._bytes[3]
    b4 = "%0.2X" % self._bytes[4]
    b5 = "%0.2X" % self._bytes[5]
    return '{0}:{1}:{2}:{3}:{4}:{5}'.format(b0, b1, b2, b3, b4, b5)

  def __getitem__(self, item):
    return self._bytes[item]

  @property
  def _as_parameter_(self):
    return self._bytes

  @property
  def raw_bytes(self):
    """
    An unsigned byte buffer view of the object (ctypes c_ubyte array).
    Use this if you need a serialized format of this object, or if you
    are marshalling data to an external C API, etc.
    """
    return self._bytes


# -----------------------------------------------------------------------------
# Lookup Entries
# -----------------------------------------------------------------------------


class Entry(object):
  """
  Represents a HEBI module. This is used by the Lookup class.
  """

  def __init__(self, name, family, mac_address):
    self._name = name
    self._family = family
    self._mac_address = mac_address

  def __str__(self):
    return 'Family: {0} Name: {1} Mac Address: {2}'.format(self._family,
      self._name, self._mac_address)

  @property
  def name(self):
    """
    :return: The name of the module.
    :rtype:  str
    """
    return self._name

  @property
  def family(self):
    """
    :return: The family to which this module belongs.
    :rtype:  str
    """
    return self._family

  @property
  def mac_address(self):
    """
    :return: The immutable MAC address of the module.
    :rtype:  str
    """
    return self._mac_address


class EntryList(UnmanagedObject):
  """
  A list of module entries. This is used by the :class:`~hebi.Lookup` class
  and is returned by :attr:`~hebi.Lookup.entrylist`.
  """
  def __init__(self, internal):
    super(EntryList, self).__init__(internal,
                                    on_delete=hebiLookupEntryListRelease)
    self._size = hebiLookupEntryListGetSize(self)
    self._iter_position = 0

  def __iter__(self):
    return self

  def __next__(self):
    return self.next()

  def next(self):
    if (self._iter_position >= self._size):
      self._iter_position = 0
      raise StopIteration
    ret = self.__get_entry(self._iter_position)
    self._iter_position = self._iter_position + 1
    return ret

  def __get_entry(self, index):
    required_size = c_size_t(0)
    if (hebiLookupEntryListGetName(self, index, c_char_p(None),
                                   byref(required_size)) != StatusSuccess):
      return None

    c_buffer = create_str(required_size.value)
    if (hebiLookupEntryListGetName(self, index, c_buffer, byref(required_size))
                                   != StatusSuccess):
      return None

    name = decode_str(c_buffer, 'utf-8')
    if (hebiLookupEntryListGetFamily(self._internal,
                                     index, c_char_p(None),
                                     byref(required_size)) != StatusSuccess):
      return None

    c_buffer = create_str(required_size.value)
    if (hebiLookupEntryListGetFamily(self._internal, index, c_buffer,
                                     byref(required_size)) != StatusSuccess):
      return None

    family = decode_str(c_buffer, 'utf-8')
    tmp_buffer = (c_ubyte * 6)()
    if (hebiLookupEntryListGetMacAddress(self._internal, index, tmp_buffer)
                                        != StatusSuccess):
      return None

    mac_address = type_utils.to_mac_address(tmp_buffer)
    return Entry(name, family, mac_address)

  def __getitem__(self, index):
    return self.__get_entry(index)


# -----------------------------------------------------------------------------
# Lookup and delegates
# -----------------------------------------------------------------------------


class LookupDelegate(UnmanagedObject):
  """
  Delegate for Lookup
  """

  def __parse_to(self, timeout_ms):
    if (timeout_ms == None):
      return Lookup.DEFAULT_TIMEOUT_MS
    else:
      try:
        return int(timeout_ms)
      except:
        raise ValueError('timeout_ms must be a number')

  def __init__(self):
    super(LookupDelegate, self).__init__(hebiLookupCreate(),
                                         on_delete=hebiLookupRelease)

  @property
  def entrylist(self):
    list = hebiCreateLookupEntryList(self)
    if (list):
      return EntryList(list)
    else:
      return None

  def get_group_from_names(self, families, names, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    families_length = len(families)
    names_length = len(names)

    families_buffer = (c_char_p * families_length)()
    families_buffer_list = [ None ] * families_length
    names_buffer = (c_char_p * names_length)()
    names_buffer_list = [ None ] * names_length

    for i, family in enumerate(families):
      family_length = len(family)+1
      families_buffer_list[i] = create_str(family, family_length)

    for i, name in enumerate(names):
      name_length = len(name)+1
      names_buffer_list[i] = create_str(name, name_length)

    for i in range(families_length):
      families_buffer[i] = cast(families_buffer_list[i], c_char_p)

    for i in range(names_length):
      names_buffer[i] = cast(names_buffer_list[i], c_char_p)

    c_char_pp = POINTER(c_char_p)
    group = c_void_p(hebiGroupCreateFromNames(self,
                                              cast(byref(families_buffer), c_char_pp),
                                              families_length,
                                              cast(byref(names_buffer), c_char_pp),
                                              names_length,
                                              timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

  def get_group_from_macs(self, addresses, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    addresses_length = len(addresses)
    addresses_list = [None] * addresses_length

    for i, address in enumerate(addresses):
      addresses_list[i] = type_utils.to_mac_address(address)

    addresses_list_c = (c_void_p * addresses_length)()
    for i in range(addresses_length):
      addresses_list_c[i] = cast(addresses_list[i].raw_bytes, c_void_p)

    group = c_void_p(hebiGroupCreateFromMacs(self, byref(addresses_list_c),
                                             addresses_length, timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

  def get_group_from_family(self, family, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    family_buffer = create_str(family, len(family)+1)
    group = c_void_p(hebiGroupCreateFromFamily(self, family_buffer, timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

  def get_connected_group_from_name(self, family, name, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    family_buffer = type_utils.create_string_buffer_compat(family, len(family)+1)
    name_buffer = type_utils.create_string_buffer_compat(name, len(name)+1)
    group = c_void_p(hebiGroupCreateConnectedFromName(self, family_buffer,
                                                      name_buffer, timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

  def get_connected_group_from_mac(self, address, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    mac_address = type_utils.to_mac_address(address)
    group = c_void_p(hebiGroupCreateConnectedFromMac(self, mac_address.raw_bytes,
                                                     timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

