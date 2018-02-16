import unittest


class LogFileTestCase(unittest.TestCase):

  def setUp(self):
    from os.path import abspath, dirname, isfile, join
    self._log1_location = join(dirname(abspath(__file__)),
                      'resources', 'log_read_smoke1.hebilog')
    self.assertTrue(isfile(self._log1_location))
    from hebi.util import load_log
    self._log1 = load_log(self._log1_location)

  def testOpenValidLogFile(self):
    # Open log file 1
    self.assertIsNotNone(self._log1)

  def testNumberOfModulesInFile(self):
    self.assertEquals(self._log1.number_of_modules, 14)

  def testGetFeedback(self):
    self.assertIsNotNone(self._log1.get_next_feedback())
    self.assertIsNotNone(self._log1.get_next_feedback())
    self.assertIsNotNone(self._log1.get_next_feedback())
    self.assertIsNotNone(self._log1.get_next_feedback())

  def testNonExistentFileThrows(self):
    from os.path import abspath, dirname, join
    from hebi.util import load_log
    with self.assertRaises(RuntimeError):
      location = join(dirname(abspath(__file__)),
                      'resources', 'NONEXISTENT.hebilog')
      result = load_log(location)
      self.fail('Unreachable statement. log file: {0}'.format(result))

  def testNoneFileThrows(self):
    from hebi.util import load_log
    with self.assertRaises(ValueError):
      result = load_log(None)
      self.fail('Unreachable statement. log file: {0}'.format(result))

  def testNonLogFileFileThrows(self):
    from os.path import abspath
    from hebi.util import load_log
    with self.assertRaises(RuntimeError):
      result = load_log(abspath(__file__))
      self.fail('Unreachable statement. log file: {0}'.format(result))


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
