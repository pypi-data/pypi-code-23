# -*- coding: utf-8 -*-
# Copyright (c) 2013 Hesky Fisher
# See LICENSE.txt for details.

"""Unit tests for CaseCat."""

import os
import unittest

from plover_casecat_dictionary import CaseCatDictionary

from plover import log, system
from plover.config import DEFAULT_SYSTEM_NAME
from plover.dictionary.base import load_dictionary
from plover.formatting import Formatter
from plover.registry import registry
from plover.steno import normalize_steno, Stroke
from plover.steno_dictionary import StenoDictionary
from plover.translation import Translator

log.set_level(log.DEBUG)

DICTIONARIES = {
        u'S-abc.sgdct': {
            'mappings': {'S': u'abc'},
            },
        u'S-abc,T-abc.sgdct': {
            'mappings': {'S': u'abc', 'T': u'abc'},
            },
        u'S-dis.sgdct': {
            'mappings': {'S': u'{dis^}'},
            },
        u'S-ing.sgdct': {
            'mappings': {'S': u'{^ing}'},
            },
        u'S_S-abc.sgdct': {
            'mappings': {'S/S': u'abc'},
            },

        # No test for "cap up", because
        # we don't yet have a genuine file
        # that contains it

        }

class CaseCatDictionaryTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        registry.update()
        system.setup(DEFAULT_SYSTEM_NAME)

    def _dictionaries_iterator(self):
        for (filename, expected) in sorted(DICTIONARIES.items()):

            dic = load_dictionary(os.path.join(os.path.dirname(__file__), filename))
            yield (filename, expected, dic)

    def test_readonly(self):

        for (filename, expected, dic) in self._dictionaries_iterator():
            self.assertTrue(dic.readonly)

    def test_load_dictionary(self):

        for (filename, expected, dic) in self._dictionaries_iterator():

            for (k, v) in expected['mappings'].items():
                self.assertEqual(dic[k], v)


