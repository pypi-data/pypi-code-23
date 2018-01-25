"""Basic behaviour tests"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import unittest
from jinja2_registry import (
    Registry,
    Renderer,
    register_loader,
    register_filesystem_loader,
    set_environment_options,
    set_environment_filters,
    set_global_defaults
)
from bs4 import BeautifulSoup

TESTING_DIR = os.path.realpath(os.path.dirname(__file__))


class TestBasic(unittest.TestCase):
    """Test basic behavior of the Jinja2 Registry"""

    template_dirs = {
        'layouts':   'templates/layouts',
        'partials':  'templates/partials',
        'pages':     'templates/pages',
    }
    layout_templates = {key: os.path.sep.join((TESTING_DIR, value))
                        for key, value in iter(template_dirs.items())}

    def setUp(self):

        for namespace, path in iter(self.layout_templates.items()):
            register_filesystem_loader(namespace, path)

    def test_complete_stack(self):
        """Test the basic behavior of the registry"""

        renderer = Renderer('pages/title.html')
        html = renderer.render()

        bs = BeautifulSoup(html, 'html.parser')

        # Confirm structure
        structure = ','.join([tag.name for tag in bs.find('html').find_all()])
        expected = 'head,title,body,ul,li,a,li,a,div,p'
        self.assertEqual(structure, expected)

        # Confirm title from "title.html"
        self.assertEqual(bs.find('title').text, 'new_title')

        # Confirm content from "content.html"
        self.assertEqual(bs.find('p').text, 'some_content')

        # Confirm navigation from "nav.html"
        linktext = [a.text for a in bs.find_all('a')]
        self.assertIn('Content page', linktext)
        self.assertIn('New title page', linktext)

    def test_defaults(self):
        """Test the context management features"""

        # Set up global context
        global_context = {
            'a': 'global',
            'b': 'global',
        }
        set_global_defaults(global_context)

        # Set up namespace context
        namespace_context = {
            'b': 'namespace',
            'c': 'namespace',
        }
        register_filesystem_loader(
            'pages',
            self.layout_templates['pages'],
            namespace_context,
        )

        # Set up class context
        class_context = {
            'c': 'class',
            'd': 'class',
        }

        class PageRenderer(Renderer):
            """Subclass of renderer with a custom namespace"""
            namespace = 'pages'
            defaults = class_context

        # Set up renderer context
        renderer_context = {
            'd': 'renderer',
            'e': 'renderer',
        }
        renderer = PageRenderer('pages/defaults.html')
        renderer.update(renderer_context)

        html = renderer.render()
        bs = BeautifulSoup(html, 'html.parser')

        # Confirm structure
        structure = ','.join([tag.name for tag in bs.find('html').find_all()])
        expected = (
            'head,title,body,ul,li,a,li,a,div,'
            'dl,dt,dd,dt,dd,dt,dd,dt,dd,dt,dd'
        )
        self.assertEqual(structure, expected)

        # Confirm default handling
        values = ','.join([
            tag.text for tag in bs.find('dl') if tag.name == 'dd'
        ])
        expected = 'global,namespace,class,renderer,renderer'
        self.assertEqual(values, expected)

    def test_environment(self):
        """Test the environment setup features"""

        options = {
            'extensions': ['jinja2.ext.with_'],
        }
        set_environment_options(options)

        filters = {
            'foo': lambda x: 'foo {}'.format(x)
        }
        set_environment_filters(filters)

        renderer = Renderer('pages/with.html')
        html = renderer.render()
        bs = BeautifulSoup(html, 'html.parser')

        # Confirm content from "with.html"
        self.assertEqual(bs.find('p').text, 'with_extension_active')
        self.assertEqual(bs.find(id='foo').text, 'foo with_extension_active')


class TestMultipleEnvironments(unittest.TestCase):
    """Test basic behaviour of the Jinja2 Registry"""

    template_dirs = {
        'layouts':   'templates/layouts',
        'partials':  'templates/partials',
        'pages':     'templates/pages',
    }
    layout_templates = {key: os.path.sep.join((TESTING_DIR, value))
                        for key, value in iter(template_dirs.items())}

    def test_different_registries(self):
        """Test the basic behavior of the registry"""

        registry = Registry()

        renderer = Renderer('pages/title.html', registry=registry)
        assert renderer.registry.environment.list_templates() == []

        for namespace, path in iter(self.layout_templates.items()):
            register_filesystem_loader(namespace, path, registry=registry)

        assert len(renderer.registry.environment.list_templates()) > 0

        assert renderer.registry is registry
        html = renderer.render()
