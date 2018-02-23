# -*- coding: utf-8 -*-

import unittest
from future.utils import with_metaclass
from classutils.singleton import SingletonType


class MySingletonClass(with_metaclass(SingletonType, object)):
    pass


class TestSingleton(unittest.TestCase):

    def setUp(self):
        self.a = MySingletonClass()
        self.b = MySingletonClass()
        self.c = MySingletonClass()

    def tearDown(self):
        pass

    def test_singleton_instantiation(self):

        self.assertEqual(self.a, self.b,
                         msg=u'Test singleton instantiation: Classes do not match!')

        self.assertEqual(self.a, self.c,
                         msg=u'Test singleton instantiation: Classes do not match!')

        self.assertEqual(self.b, self.c,
                         msg=u'Test singleton instantiation: Classes do not match!')


if __name__ == u'__main__':
    unittest.main()
