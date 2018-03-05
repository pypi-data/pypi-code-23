# -*- coding: utf-8 -*-

import unittest

from tapioca_cloudez import Cloudez


class TestTapiocaCloudez(unittest.TestCase):

    def setUp(self):
        self.wrapper = Cloudez()


if __name__ == '__main__':
    unittest.main()
