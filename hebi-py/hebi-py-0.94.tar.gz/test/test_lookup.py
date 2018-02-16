import unittest


class LookupTestCase(unittest.TestCase):
  # TODO: We should make these tests instrumentation tests, as we can't really simulate a network connection
  pass


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
