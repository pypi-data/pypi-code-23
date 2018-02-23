#!/usr/bin/env python3
# coding=utf-8

"""
@version:1.0.0
@author: ysicing
@file: Ding/dbot_test.py
@time: 23/02/2018 11:30
"""

import unittest

from dbot import DtalkBot


class TestDtalkBot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.webhook = 'https://oapi.dingtalk.com/robot/send?access_token=2d3e7d42f8e15e90665fc08f7954619f040b46f2ac77dea364db304b815f6bee'
        cls.bot = DtalkBot(cls.webhook)

    def send_mgs(self):
        result = self.bot.msg("test")
        self.assertEqual(result['errcode'], 0)


if __name__ == '__main__':
    unittest.main()