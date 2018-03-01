# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See http://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
"""
Internally used procedures to convert from and to types. Functions here aren't
part of the public API and may change without notice.
"""

from ctypes import Array, create_string_buffer
from numpy import float64, asmatrix, ascontiguousarray, matrix
from sys import version_info

def __mac_address_from_bytes(a, b, c, d, e, f):
  """
  Used internally by ``to_mac_address``
  """
  from .lookup import MacAddress
  return MacAddress(int(a), int(b), int(c), int(d), int(e), int(f))


def __mac_address_from_string(address):
  """
  Used internally by `to_mac_address`
  """
  from .lookup import MacAddress
  if (type(address) != str):
    try:
      address = str(address)
    except:
      raise ValueError('Input must be string or convertible to string')

  import re
  match = re.match(r'^(([a-fA-F0-9]{2}):){5}([a-fA-F0-9]{2})$', address)
  if (match != None):
    mac_byte_a = int(address[0:2], 16)
    mac_byte_b = int(address[3:5], 16)
    mac_byte_c = int(address[6:8], 16)
    mac_byte_d = int(address[9:11], 16)
    mac_byte_e = int(address[12:14], 16)
    mac_byte_f = int(address[15:17], 16)
    return MacAddress(mac_byte_a, mac_byte_b, mac_byte_c,
                      mac_byte_d, mac_byte_e, mac_byte_f)
  else:
    raise ValueError('Unable to parse mac address'
                     ' from string {0}'.format(address))


def to_mac_address(*args):
  """
  Convert input argument(s) to a MacAddress object.
  Only 1 or 6 arguments are valid.

  If 1 argument is provided, try the following:

    * If input type is MacAddress, simply return that object
    * If input type is list or ctypes Array, recall with these elements
    * If input is of another type, try to parse a MAC address from its
      `__str__` representation

  When 6 parameters are provided, this attempts to construct a MAC address
  by interpreting the input parameters as sequential bytes of a mac address.

  If the provided argument count is neither 1 or 6,
  this function throws an exception.

  :param args: 1 or 6 element list of variadic arguments
  :return: a MacAddress instance
  """
  from .lookup import MacAddress

  if (len(args) == 1):
    if (type(args[0]) == MacAddress):
      return args[0]
    elif(isinstance(args[0], list) or isinstance(args[0], Array)):
      if (len(args[0]) == 1):
        return to_mac_address(args[0])
      elif(len(args[0]) == 6):
        arg = args[0]
        return to_mac_address(*arg)
      else:
        raise ValueError('Invalid amount of arguments provided'
                         ' ({0}). Expected 1 or 6'.format(len(args[0])))
    else:
      try:
        return __mac_address_from_string(args[0])
      except ValueError as v:
        raise ValueError('Could not create mac address from argument', v)
  elif (len(args) == 6):
    return __mac_address_from_bytes(*args)
  else:
    raise ValueError('Invalid amount of arguments provided'
                     ' ({0}). Expected 1 or 6'.format(len(args)))


def is_matrix_or_matrix_convertible(val):
  """
  Used internally to determine if the input is or is convertible to a matrix.

  Note that while an Array ( [1, N] or [N, 1] ) can also be a matrix,
  we define a matrix here to be a two dimensional Array such that
  both its rows and columns are both *greater* than 1.
  """
  if (isinstance(val, matrix)):
    shape = val.shape
    if (shape[0] == 1 or shape[1] == 1):
      return False
    return True
  try:
    m = asmatrix(val)
    if (m.shape[0] == 1 or m.shape[1] == 1):
      return False
    return True
  except:
    return False


# -----------------------------------------------------------------------------
# Converting to numpy types
# -----------------------------------------------------------------------------


def to_contig_sq_mat(mat, dtype=float64, size=3):
  """
  Converts input to a numpy square matrix of the specified data type and size.

  This function ensures that the underlying data is laid out
  in contiguous memory.

  :param mat: Input matrix
  :param dtype: Data type of matrix
  :param size: Size of matrix
  :return: a `size`x`size` numpy matrix with elements of type `dtype`
  """
  try:
    size = int(size)
  except Exception as e:
    raise ValueError('size must be convertible to an integer', e)

  if (size < 1):
    raise ValueError('size must be greater than zero')

  ret = asmatrix(mat, dtype=dtype)

  # Is array-like
  if (ret.shape[0] == 1):
    # Will fail if not len of `size`*`size`
    ret = ret.reshape(size, size)

  # Enforce output will be right shape
  if (ret.shape != (size, size)):
    raise ValueError('Cannot convert input to shape {0}'.format((size, size)))

  # Enforce contiguous in memory
  if not ret.flags['C_CONTIGUOUS']:
    ret = ascontiguousarray(ret)

  return ret


# -----------------------------------------------------------------------------
# CTypes Compatibility functions
# -----------------------------------------------------------------------------

if (version_info[0] == 2):

  create_string_buffer_compat = create_string_buffer

  def decode_string_buffer(bfr, encoding='utf8'):
    import ctypes
    if (type(bfr) == str):
      return bfr
    elif isinstance(bfr, ctypes.Array):
      return ctypes.cast(bfr, ctypes.c_char_p).value
    else:
      raise TypeError(bfr)


  def __is_int_type(val):
    return isinstance(val, (int, long))


else:

  def create_string_buffer_compat(init, size=None):
    if(size == None):
      if isinstance(init, str):
        return create_string_buffer(bytes(init, 'utf8'))
      elif isinstance(init, int):
        return create_string_buffer(init)
    else:
      return create_string_buffer(bytes(init, 'utf8'), size)


  def decode_string_buffer(bfr, encoding='utf8'):
    """
    Enables compatibility between Python 2 and 3

    :param bfr: a string, ``bytes``, or ctypes array
    :return: a string
    """
    import ctypes
    if (type(bfr) == str):
      return bfr
    elif isinstance(bfr, bytes):
      return bfr.decode(encoding)
    elif isinstance(bfr, ctypes.Array):
      return ctypes.cast(bfr, ctypes.c_char_p).value.decode(encoding)
    else:
      raise TypeError(bfr)


  def __is_int_type(val):
    return isinstance(val, int)


def create_double_buffer(size):
  """
  Creates a ctypes array of c_double elements

  :param size: The number of elements to be in the array
  :return: c_double array
  """
  if not __is_int_type(size):
    raise TypeError('size must be an integer')

  if (size < 1):
    raise ValueError('size must be a positive number')

  from ctypes import c_double
  return (c_double * size)()
