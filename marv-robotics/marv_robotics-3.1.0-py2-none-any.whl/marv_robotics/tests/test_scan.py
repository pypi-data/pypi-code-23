# -*- coding: utf-8 -*-
#
# This file is part of MARV Robotics
#
# Copyright 2016-2018 Ternaris
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

import unittest

from marv.scanner import DatasetInfo as DSI
from marv_robotics.bag import scan


class TestCase(unittest.TestCase):
    maxDiff = None

    def test_nonbag(self):
        rv = scan('/', [''], ['a', 'b'])
        self.assertEqual(rv, [])

    def test_single_bags(self):
        rv = scan('/', [''], ['foo.bag', 'bar.bag'])
        self.assertEqual(rv, [DSI(name='foo', files=['foo.bag']),
                              DSI(name='bar', files=['bar.bag'])])

    def test_rosbag_sets(self):
        rv = scan('/', [''], ['set0_0000-00-00-00-00-00_0.bag',
                              'set0_0000-01-00-00-00-00_1.bag',
                              'set0_0000-02-00-00-00-00_2.bag',
                              'set1_0000-00-00-00-00-00_0.bag',
                              'set1_0000-01-00-00-00-00_1.bag',
                              'set1_0000-02-00-00-00-00_2.bag',
                              'set2.bag',
                              'set2_0000-00-00-00-00-00_0.bag',
                              'set2_0000-00-00-00-00-00_1.bag',
                              'set2_0000-00-00-00-00-00_2.bag'])
        self.assertEqual(rv, [
            DSI(name='set0', files=['set0_0000-00-00-00-00-00_0.bag',
                                    'set0_0000-01-00-00-00-00_1.bag',
                                    'set0_0000-02-00-00-00-00_2.bag']),
            DSI(name='set1', files=['set1_0000-00-00-00-00-00_0.bag',
                                    'set1_0000-01-00-00-00-00_1.bag',
                                    'set1_0000-02-00-00-00-00_2.bag']),
            DSI(name='set2', files=['set2.bag']),
            DSI(name='set2', files=['set2_0000-00-00-00-00-00_0.bag',
                                    'set2_0000-00-00-00-00-00_1.bag',
                                    'set2_0000-00-00-00-00-00_2.bag'])
        ])

    def test_scan_broken_set_edge_cases(self):
        rv = scan('/', [''], ['set0_0000-00-00-00-00-00_0.bag',
                              'set0_0000-00-00-00-00-00_2.bag',
                              'set1_0000-00-00-00-00-00_1.bag',
                              'set1_0000-00-00-00-00-00_2.bag',
                              'set2.bag',
                              'set2_0000-00-00-00-00-00_1.bag',
                              'set2_0000-00-00-00-00-00_2.bag'])
        self.assertEqual(rv, [
            DSI(name='set0', files=['set0_0000-00-00-00-00-00_0.bag']),
            DSI(name='set0_0000-00-00-00-00-00_2', files=['set0_0000-00-00-00-00-00_2.bag']),
            DSI(name='set1_0000-00-00-00-00-00_1', files=['set1_0000-00-00-00-00-00_1.bag']),
            DSI(name='set1_0000-00-00-00-00-00_2', files=['set1_0000-00-00-00-00-00_2.bag']),
            DSI(name='set2', files=['set2.bag']),
            DSI(name='set2_0000-00-00-00-00-00_1', files=['set2_0000-00-00-00-00-00_1.bag']),
            DSI(name='set2_0000-00-00-00-00-00_2', files=['set2_0000-00-00-00-00-00_2.bag']),
        ])

    def test_without_timestamp(self):
        rv = scan('/', [''], ['foo_0.bag', 'foo_1.bag', 'foo_3.bag', 'foo_4.bag'])
        self.assertEqual(rv, [DSI(name='foo', files=['foo_0.bag', 'foo_1.bag']),
                              DSI(name='foo_3', files=['foo_3.bag']),
                              DSI(name='foo_4', files=['foo_4.bag'])])

    def test_mixed_edge_cases(self):
        rv = scan('/', [''], ['set0_0000-00-00-00-00-00_0.bag',
                              'set0_1.bag',
                              'set0_1000-00-00-00-00-00_2.bag'])
        self.assertEqual(rv, [
            DSI(name='set0', files=['set0_0000-00-00-00-00-00_0.bag']),
            DSI(name='set0_1', files=['set0_1.bag']),
            DSI(name='set0_1000-00-00-00-00-00_2', files=['set0_1000-00-00-00-00-00_2.bag']),
        ])

    def test_missing_index(self):
        rv = scan('/', [''], ['foo_0000-11-00-00-00-00.bag',
                              'foo_0000-22-00-00-00-00.bag'])
        self.assertEqual(rv, [
            DSI(name='foo_0000-11-00-00-00-00', files=['foo_0000-11-00-00-00-00.bag']),
            DSI(name='foo_0000-22-00-00-00-00', files=['foo_0000-22-00-00-00-00.bag']),
        ])
