#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property
from hamcrest import contains_inanyorder

import os
import time
import unittest

from nti.recipes.json import Recipe


class TestRecipe(unittest.TestCase):

    def setUp(self):
        self.name = 'test'
        self.buildout = {}
        self.buildout[self.name] = {}
        self.buildout[self.name]['output-file'] = 'foo.json'
        self.buildout[self.name]['contents-section'] = 'test-main'
        self.buildout[self.name]['recipe'] = 'nti.recipe.json'

        contents_section = self.buildout[self.name]['contents-section']
        self.buildout[contents_section] = {}
        self.buildout[contents_section]['foo'] = "foo"
        self.buildout[contents_section]['bar'] = "bar"
        self.buildout[contents_section]['foo_bool'] = "true"
        self.buildout[contents_section]['bar_bool'] = "False"
        self.buildout[contents_section]['baz-section'] = "test-baz"
        self.buildout[contents_section]['bazbaz-section'] = "test-bazbaz"

        self.buildout[contents_section]['node-section'] = "node-section"
        self.buildout[contents_section]['external-libraries'] = "external-libraries"

        baz_section = self.buildout[contents_section]['baz-section']
        self.buildout[baz_section] = {}
        self.buildout[baz_section]['foo'] = "foo"
        self.buildout[baz_section]['bar'] = "bar"
        self.buildout[baz_section]['baz'] = "baz"
        self.buildout[baz_section]['foobar'] = """line 1
        test-bazbaz-section
        line 3
        line 4"""
        bazbaz_section = self.buildout[contents_section]['bazbaz-section']
        self.buildout[bazbaz_section] = {}
        self.buildout[bazbaz_section]['foo'] = "myfoo"

        node_section = self.buildout[contents_section]['node-section']
        self.buildout[node_section] = {}
        self.buildout[node_section]['jquery-section'] = "external-libraries"

        external_section = self.buildout[contents_section]['external-libraries']
        self.buildout[external_section] = {
            'requires': '\n'.join(['jquery', 'stripe', '**end-list**']),
            'definesSymbol':  'jQuery.payment'
        }

    def test_recipe(self):
        recipe = Recipe(self.buildout, self.name, self.buildout[self.name])
        assert_that(recipe,
                    has_property('contents',
                                 has_entries('foo', 'foo',
                                             'bar', 'bar',
                                             'foo_bool', True,
                                             'bar_bool', False,
                                             'baz', is_(not_none()),
                                             'node', is_(not_none()),
                                             'bazbaz', is_(not_none()))))
        assert_that(recipe.contents['baz'],
                    has_entries('foo', 'foo',
                                'bar', 'bar',
                                'baz', 'baz',
                                'foobar', contains_inanyorder('line 1', {'foo': 'myfoo'}, 'line 3', 'line 4')))

        assert_that(recipe.contents['baz'],
                    has_entries('foo', 'foo',
                                'bar', 'bar',
                                'baz', 'baz',
                                'foobar', contains_inanyorder('line 1', {'foo': 'myfoo'}, 'line 3', 'line 4')))
        assert_that(recipe.contents['bazbaz'],
                    has_entries('foo', 'myfoo'))

        assert_that(recipe.contents['node'],
                    has_entries('jquery',
                                has_entries('definesSymbol', 'jQuery.payment',
                                            'requires', ['jquery', 'stripe'])))

    def test_install(self):
        name = "%s_%s" % (self.name, time.time())
        recipe = Recipe(self.buildout, name, self.buildout[self.name])
        filename = recipe.filename
        try:
            recipe.install()
            assert_that(os.path.exists(filename), is_(True))
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_update(self):
        name = "%s_%s" % (self.name, time.time())
        recipe = Recipe(self.buildout, name, self.buildout[self.name])
        filename = recipe.filename
        try:
            recipe.update()
            assert_that(os.path.exists(filename), is_(True))
        finally:
            if os.path.exists(filename):
                os.unlink(filename)
