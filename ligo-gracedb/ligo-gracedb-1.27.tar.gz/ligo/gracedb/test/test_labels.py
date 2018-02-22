# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import unittest
import os
import time
from test import TestGraceDb

class TestLabels(TestGraceDb):
    """A suite for carefully testing event creation with labels"""

    # Helper functions --------------------------------------------------------
    def label_creation_helper(self, input_labels=None):
        time.sleep(self.SLEEP_TIME)
        eventFile = os.path.join(self.TEST_DATA_DIR, "burst-cwb.txt")
        if input_labels:
            r = self._gracedb.createEvent("Test", "CWB", eventFile,
                labels=input_labels)
        else:
            r = self._gracedb.createEvent("Test", "CWB", eventFile)
        result = r.json()
        gid = result['graceid']

        # Make sure event was created properly
        self.assertEqual(r.status, 201)

        # Make sure there are no warnings
        self.assertEqual(result['warnings'], [])

        # Get event and make sure labels match what we expect
        event_labels = self._gracedb.labels(gid).json()['labels']
        if input_labels:
            # Make sure that input_labels is a list for ease of comparison
            if isinstance(input_labels, str):
                input_labels = [input_labels]

            event_label_names = [l['name'] for l in event_labels]
            for l in input_labels:
                self.assertIn(l, event_label_names)
        else:
            self.assertEqual(event_labels, [])

    def label_bad_args_helper(self, input_labels, error_class):
        eventFile = os.path.join(self.TEST_DATA_DIR, "burst-cwb.txt")

        with self.assertRaises(error_class):
            r = self._gracedb.createEvent("Test", "CWB", eventFile,
                labels=input_labels)

    # Tests -------------------------------------------------------------------
    def test_create_event_with_label(self):
        """Create an event with a single label"""
        self.label_creation_helper("DQV")

    def test_create_event_with_labels(self):
        """Create an event with multiple labels"""
        self.label_creation_helper(["DQV","INJ","PE_READY"])

    def test_create_event_with_label_blank_string(self):
        """Create an event with labels=''"""
        self.label_creation_helper('')

    def test_create_event_with_label_empty_list(self):
        """Create an event with labels=[]"""
        self.label_creation_helper([])

    def test_create_event_no_labels_defined(self):
        """Try to create an event with no labels defined"""
        self.label_creation_helper()

    def test_create_event_label_list_empty_string(self):
        """Try to create an event with labels=['']"""
        self.label_bad_args_helper([''], NameError)

    def test_create_event_label_string_bad(self):
        """Try to create an event with labels='BADLABEL'"""
        self.label_bad_args_helper('BADLABEL', NameError)

    def test_create_event_label_list_bad(self):
        """Try to create an event with labels=['BADLABEL']"""
        self.label_bad_args_helper(['BADLABEL'], NameError)

    def test_create_event_label_list_onebad(self):
        """Try to create an event with labels=['H1OPS','BADLABEL']"""
        self.label_bad_args_helper(['H1OPS','BADLABEL'], NameError)

    def test_create_event_label_list_allbad(self):
        """Try to create an event with labels=['BAD1','BAD2']"""
        self.label_bad_args_helper(['BAD1','BAD2'], NameError)

    def test_create_event_label_int(self):
        """Try to create an event with labels=123"""
        self.label_bad_args_helper(123, TypeError)


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
