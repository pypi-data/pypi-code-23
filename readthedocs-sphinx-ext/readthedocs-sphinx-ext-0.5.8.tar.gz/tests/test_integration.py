import unittest

from readthedocs_ext.readthedocs import HtmlBuilderMixin

from .util import sphinx_build, build_output


class LanguageIntegrationTests(unittest.TestCase):

    def _run_test(self, test_dir, test_file, test_string, builder='html'):
        with build_output(test_dir, test_file, builder) as data:
            self.assertIn(test_string, data)


class IntegrationTests(LanguageIntegrationTests):

    def test_integration(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'Hey there friend!',
            builder='readthedocs',
        )

    def test_media_integration(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'media.readthedocs.org',
            builder='readthedocs',
        )

    def test_included_js(self):
        self._run_test(
            'pyexample',
            '_build/readthedocs/index.html',
            'readthedocs-dynamic-include.js',
            builder='readthedocs',
        )

    def test_replacement_pattern(self):
        pattern = HtmlBuilderMixin.REPLACEMENT_PATTERN
        src = "$(document).ready(function() {\n  Search.init();\n});"
        self.assertRegexpMatches(src, pattern)
        # Minor changes to spacing, just to ensure rule is correct. This should
        # never happen as this block of code is 10 years old
        src = "$(document).ready(function    ()     {\n    Search.init();\n});"
        self.assertRegexpMatches(src, pattern)

    def test_searchtools_is_patched(self):
        with build_output('pyexample', '_build/readthedocs/_static/searchtools.js',
                          builder='readthedocs') as data:
            self.assertNotIn('Search.init();', data)
            self.assertNotRegexpMatches(
                data,
                HtmlBuilderMixin.REPLACEMENT_PATTERN
            )
            self.assertIn(HtmlBuilderMixin.REPLACEMENT_TEXT, data)
