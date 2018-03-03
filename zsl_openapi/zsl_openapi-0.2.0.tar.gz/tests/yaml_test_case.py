import os
from unittest import TestCase

import jinja2
import yaml


class YAMLTestCase(TestCase):

    def renderTemplate(self, name, context=None):
        if context is None:
            context = {}
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        )
        template = env.get_template(name, context)
        return template.render(context)

    def thenYAMLShouldBeEqual(self, template, result, message, template_context=None):
        expected_result = self.renderTemplate(template, template_context)
        yaml_expected = yaml.load(expected_result)
        yaml_computed = yaml.load(result)
        self.assertEqual(yaml_expected, yaml_computed, message)
