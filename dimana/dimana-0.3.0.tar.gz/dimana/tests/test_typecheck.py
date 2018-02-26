import unittest
from dimana._typecheck import typecheck


class typecheckTests (unittest.TestCase):
    def test_ok(self):
        typecheck(3, int)

    def test_failure(self):
        self.assertRaises(TypeError, typecheck, 3, str)
