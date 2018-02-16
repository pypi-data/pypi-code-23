import unittest

import ctypes
import numpy

def check_binary_mac_address(a, b):
  if (len(a) != len(b) or len(a) != 6):
    return False, 'len(a)={0} len(b)={1}'.format(len(a), len(b))
  for i in range(0, 6):
    if (a[i] != b[i]):
      return False, 'a[{0}]={1} != b[{0}]={2}'.format(i, a[i], b[i])
  return True, ''


class ParseMacAddressTestCase(unittest.TestCase):

  def __verify_result(self, res, expect):
    from hebi._internal.lookup import MacAddress
    self.assertIsNotNone(res)
    self.assertIsInstance(res, MacAddress)
    ok, msg = check_binary_mac_address(res.raw_bytes, expect)
    self.assertIs(ok, True, msg)

  def __test_input1(self, arg, expect):
    from hebi._internal.type_utils import to_mac_address as mac_address
    self.__verify_result(mac_address(arg), expect)

  def __test_inputN(self, arg, expect):
    from hebi._internal.type_utils import to_mac_address as mac_address
    self.__verify_result(mac_address(*arg), expect)

  def testHumanReadableStringParse(self):
    arg = '00:00:00:00:00:00'
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)

  def testIntListParse(self):
    arg = [0, 0, 0, 0, 0, 0]
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)
    self.__test_inputN(arg, expect)

  def testStringToIntListParse(self):
    arg = ['0', '0', '0', '0', '0', '0']
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)
    self.__test_inputN(arg, expect)

  def testCTypesCByte(self):
    arg = (ctypes.c_byte * 6)(*[0, 0, 0, 0, 0, 0])
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)
    self.__test_inputN(arg, expect)

  def testCTypesCUByte(self):
    arg = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)
    self.__test_inputN(arg, expect)

  def testDirectMacAddressType(self):
    from hebi._internal.lookup import MacAddress
    arg = MacAddress(0, 0, 0, 0, 0, 0)
    expect = (ctypes.c_ubyte * 6)(*[0, 0, 0, 0, 0, 0])
    self.__test_input1(arg, expect)
    self.__test_inputN(arg, expect)

  def testFailTwoArgs(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = [0, 0]
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

    with self.assertRaises(ValueError):
      res = mac_address(*arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailSevenArgs(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = [0, 0, 0, 0, 0, 0, 0]
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

    with self.assertRaises(ValueError):
      res = mac_address(*arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailNullArg(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = None
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailInvalidString(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = 'INVALID_STRING' # Literally, Invalid String
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailInvalidInputType(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = dict()
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailMalformedMacString1(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = '00:00:00:00:00:'
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailMalformedMacString2(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = '00:00:00:00:00:0'
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))

  def testFailMalformedMacString3(self):
    from hebi._internal.type_utils import to_mac_address as mac_address
    arg = 'zz:zz:zz:zz:zz:zz'
    with self.assertRaises(ValueError):
      res = mac_address(arg)
      self.fail('Unreachable statement. Created MacAddress is: {0}'.format(res))


class MatrixConvertibleTestCase(unittest.TestCase):

  def testNonNumericString(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat('I am a fish'))

  def testNumericNonStrippedNonSquareMatrixString(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat(' 42, 42 '))

  def testOneElementSquareMatrixString(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat('42'))

  def testOneElementSquareMatrixInt(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat(42))

  def testOneElementSquareMatrixFloat(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat(42.0))

  def testOneElementSquareMatrixIntList(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat([42]))

  def testTwoElementSquareMatrixIntList(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat([42, 42]))

  def testTwoElementNonSquareMatrixCtypesArray(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat((ctypes.c_double * 2)(*[42, 42])))

  def testTwoElementNonSquareMatrixMatrix(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat(numpy.matrix([42, 42])))

  def testFourElementNonSquareMatrixMatrix(self):
    # NOTE: The shape matters. if we pass in [[42, 42], [42, 42]], this is
    # expected to be ``True``!
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertFalse(is_mat(numpy.matrix([42, 42, 42, 42])))

  def testFourElementSquareMatrixString(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertTrue(is_mat('42, 11; 22, 33'))

  def testFourElementSquareMatrixNonStrippedString(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertTrue(is_mat('  42, 43  ; 41, 16  '))

  def testFourElementSquareMatrixIntListList(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertTrue(is_mat([[0, 3], [1, 2]]))

  def testFourElementSquareMatrixCtypesArrayList(self):
    from hebi._internal.type_utils import is_matrix_or_matrix_convertible as is_mat
    self.assertTrue(is_mat([(ctypes.c_double * 2)(*[0, 3]), (ctypes.c_double * 2)(*[1, 2])]))


class ToContiguousMatrixTestCase(unittest.TestCase):

  def __assert_valid(self, val, size, dtype):
    from hebi._internal.type_utils import to_contig_sq_mat as to_mat
    from numpy import matrix
    result = to_mat(val, dtype, size)
    self.assertIsNotNone(result)
    self.assertIsInstance(result, matrix)
    self.assertEqual(result.shape[0], size, 'Unexpected row size')
    self.assertEqual(result.shape[1], size, 'Unexpected column size')
    self.assertTrue(result.flags['C_CONTIGUOUS'],
                    'Matrix is not contiguous'
                    '(C_CONTIGUOUS flag is False)')

  def __assert_invalid(self, val, size, dtype, except_type):
    from hebi._internal.type_utils import to_contig_sq_mat as to_mat
    with self.assertRaises(except_type):
      result = to_mat(val, dtype, size)
      self.fail('Unreachable statement. Created Matrix is: {0}'.format(result))

  def testValid1(self):
    # 1 element matrix (which is valid)
    self.__assert_valid([1.0], 1, numpy.float32)

  def testValid2(self):
    # Reshape array
    self.__assert_valid([1.0, 1.0, 1.0, 1.0], 2, numpy.float32)

  def testValid3(self):
    # List of lists
    self.__assert_valid([[1.0, 1.0], [1.0, 1.0]], 2, numpy.float32)

  def testValid4(self):
    # Same as #3, but different data type
    self.__assert_valid([[1.0, 1.0], [1.0, 1.0]], 2, numpy.float64)

  def testValid5(self):
    # Python syntactic sugar compatibility
    self.__assert_valid([1.0] * 9, 3, numpy.float64)

  def testValid6(self):
    # Same as #5, but for input which doesn't need to be reshaped
    self.__assert_valid([[1.0] * 3] * 3, 3, numpy.float64)

  def testValid7(self):
    # Integer matrix
    self.__assert_valid([1.0] * 9, 3, numpy.uint32)

  def testValid8(self):
    # MATLAB-like array as string reshaped
    self.__assert_valid('1.0, 1.0, 1.0, 1.0', 2, numpy.float32)

  def testValid9(self):
    # MATLAB-like matrix as string
    self.__assert_valid('1.0, 1.0; 1.0, 1.0', 2, numpy.float32)

  def testValid10(self):
    # ctypes array reshaped
    self.__assert_valid((ctypes.c_double * 4)(*[1.0, 2.0, 3.0, 4.0]), 2, numpy.float32)

  def testInvalid1(self):
    # Non-Square matrix
    self.__assert_invalid([1.0, 1.0], 1, numpy.float32, ValueError)

  def testInvalid2(self):
    # Negative size parameter
    self.__assert_invalid([1.0, 1.0], -1, numpy.float32, ValueError)

  def testInvalid3(self):
    # ``None`` as matrix parameter
    self.__assert_invalid(None, 2, numpy.float32, ValueError)

  def testInvalid4(self):
    # Invalid Type parameter (literally)
    self.__assert_invalid([1.0], 1, 'Invalid Type', TypeError)

  def testInvalid5(self):
    # Size mismatch
    self.__assert_invalid([1.0], 4, numpy.float32, ValueError)

  def testInvalid6(self):
    # Mathematic expression
    self.__assert_invalid('1.0 + 1.0', 1, numpy.float64, SyntaxError)

  def testInvalid7(self):
    # Non-Numeric string
    self.__assert_invalid('==41_$132agds', 1, numpy.float64, SyntaxError)


class CreateStringBufferTestCase(unittest.TestCase):
  # TODO: test invalid cases

  def __verify_valid(self, actual, expect_str, expect_size):
    from ctypes import Array
    self.assertIsNotNone(actual)
    self.assertIsInstance(actual, Array)

    import sys
    if (sys.version_info[0] == 2):
      actual_str = actual.value
    else:
      actual_str = actual.value.decode('utf8')

    self.assertEqual(actual_str, expect_str)
    self.assertEqual(len(actual), expect_size)

  def testValid1(self):
    # verify buffer is length of string + 1 (for null character)
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo')
    self.__verify_valid(actual, 'foo', 4)

  def testValid2(self):
    # verify buffer is length of string, as is specified by 2nd param
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo', 3)
    self.__verify_valid(actual, 'foo', 3)

  def testValid3(self):
    # verify buffer is length provided, which is larger than string + 1
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo', 42)
    self.__verify_valid(actual, 'foo', 42)

  def testValid4(self):
    # verify buffer is length provided, with empty (zero'd out memory) string
    # TODO: actually go over memory of the length & verify all of it == 0
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer(42)
    self.__verify_valid(actual, '', 42)


class DecodeStringBufferTestCase(unittest.TestCase):
  # TODO: test invalid cases

  def __verify_valid(self, actual, expected):
    from hebi._internal.type_utils import decode_string_buffer as decode_buffer
    actual_decoded = decode_buffer(actual)
    self.assertIsInstance(actual_decoded, str)
    self.assertEqual(actual_decoded, expected)

  def testValid1(self):
    # string buffer with null terminating char
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo')
    self.__verify_valid(actual, 'foo')
  
  def testValid2(self):
    # string buffer without null terminating char
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo', 3)
    self.__verify_valid(actual, 'foo')

  def testValid3(self):
    # string buffer with buffer larger than string + null character
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer('foo', 42)
    self.__verify_valid(actual, 'foo')

  def testValid4(self):
    # string buffer with empty string
    from hebi._internal.type_utils import create_string_buffer_compat as create_buffer
    actual = create_buffer(42)
    self.__verify_valid(actual, '')

  def testValid5(self):
    # Identity Case (literally)
    self.__verify_valid('Identity Case', 'Identity Case')


class CreateDoubleCtypesBufferTestCase(unittest.TestCase):

  def __verify_valid(self, arg, expect_length):
    from hebi._internal.type_utils import create_double_buffer as create_buffer
    result = create_buffer(arg)
    self.assertIsNotNone(result)
    self.assertIsInstance(result, ctypes.Array)
    self.assertEqual(len(result), expect_length)

  def __verify_invalid(self, arg, expect_except):
    from hebi._internal.type_utils import create_double_buffer as create_buffer
    with self.assertRaises(expect_except):
      result = create_buffer(arg)
      self.fail('Unreachable statement. Buffer: {0}'.format(result))

  def testSingleElement(self):
    # Verify we can create 1 element array
    self.__verify_valid(1, 1)

  def testMultipleElement(self):
    # Verify we can create > 1 element array (most common use case)
    self.__verify_valid(16, 16)

  def testFailOnZeroLength(self):
    # Zero length should throw
    self.__verify_invalid(0, ValueError)

  def testFailOnNegativeLength(self):
    # Negative length should throw
    self.__verify_invalid(-1, ValueError)

  def testFailOnFloatLength(self):
    # Float length should throw
    self.__verify_invalid(42.0, TypeError)

  def testFailOnStringLength(self):
    # String length should throw
    self.__verify_invalid('42', TypeError)

  def testFailOnNoneLength(self):
    # ``None`` for length should throw
    self.__verify_invalid(None, TypeError)


def __load_hebi():
  # Force add the current directory as a package, which will in return
  # import the `hebi` package from this repository, taking precedence over
  # any user installed variant of the hebi-py API
  if __package__ == None:
    from os.path import abspath, dirname
    from importlib import import_module
    import sys
    sys.path = [dirname(dirname(abspath(__file__)))] + sys.path
    import_module('test')


def main():
  __load_hebi()
  unittest.main()


if __name__ == '__main__':
  main()
