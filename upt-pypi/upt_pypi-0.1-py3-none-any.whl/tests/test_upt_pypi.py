# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
from unittest import mock
import unittest

from upt import PackageRequirement
from upt_pypi.upt_pypi import PyPIFrontend


class TestPyPIFrontend(unittest.TestCase):
    def setUp(self):
        self.parser = PyPIFrontend()

    def test_compute_requirements_invalid_json(self):
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data='{}'):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
        self.assertEqual(reqs, {})

    def test_compute_requirements_no_requirements(self):
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data='{}'):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertEqual(reqs, {})

    def test_compute_requirements_from_metadata_json(self):
        data = '''\
{
   "run_requires": [
      {
         "requires": [
            "foo (>3.14)",
            "bar"
         ]
      }
    ],
   "test_requires": [
      {
         "requires": [
            "pytest"
         ]
      }
    ]
}'''
        expected = {
            'run': [
                PackageRequirement('foo', '>3.14'),
                PackageRequirement('bar')
            ],
            'test': [
                PackageRequirement('pytest')
            ],
        }
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data=data):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertDictEqual(reqs, expected)

    def test_compute_requirements_from_metadata_json_ignore_extras(self):
        data = '''\
{
   "run_requires": [
      {
         "requires": [
            "foo (>3.14)",
            "bar"
         ]
      },
      {
         "extra": "some-nice-feature",
         "requires": [
            "baz"
         ]
      }
    ]
}'''
        expected = {
            'run': [
                PackageRequirement('foo', '>3.14'),
                PackageRequirement('bar')
            ]
        }
        with mock.patch('builtins.open', new_callable=mock.mock_open,
                        read_data=data):
            reqs = self.parser.compute_requirements_from_metadata_json('fname')
            self.assertDictEqual(reqs, expected)


if __name__ == '__main__':
    unittest.main()
