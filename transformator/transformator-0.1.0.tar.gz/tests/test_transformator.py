from collections import OrderedDict
from unittest import TestCase
from unittest.mock import Mock, patch

from transformator.transformator import Transformator


class TestTransformator(TestCase):
    def assertTransformated(self, transformations, container, expected):
        actual = Transformator(transformations).transform(container)
        self.assertDictEqual(actual, expected)

    def test_empty_transformations(self):
        transformations = {}
        container = {'key1': 1}
        self.assertTransformated(transformations, container, container)

    def test_empty_container(self):
        transformations = {'key1': 'new_key1'}
        container = {}
        self.assertTransformated(transformations, container, container)

    def test_empty_container_and_transformations(self):
        transformations = {}
        container = {}
        self.assertTransformated(transformations, container, container)

    def test_flat_keys(self):
        transformations = {
            'key1': 'new_key1',
            'key3': 'new_key3',
        }
        container = {
            'key1': 1,
            'key2': 2,
        }
        expected = {
            'new_key1': 1,
            'key2': 2,
        }
        self.assertTransformated(transformations, container, expected)

    def test_composite_keys(self):
        transformations = {
            'key1': 'new_key1',
            'key2.key3': 'new_key23',
        }
        container = {
            'key1': 1,
            'key2': {
                'key3': 23,
            },
        }
        expected = {
            'new_key1': 1,
            'key2': {
                'new_key23': 23,
            },
        }
        self.assertTransformated(transformations, container, expected)
