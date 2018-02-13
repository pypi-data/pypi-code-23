import unittest
from . import test_oar


def oar_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_oar)
    return suite
