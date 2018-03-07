# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import unittest

import requests_mock

import upt
from upt_cpan.upt_cpan import CPANFrontend


class TestCPANFrontend(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()

    def test_invalid_package_name(self):
        with self.assertRaises(upt.InvalidPackageNameError):
            self.frontend.parse('probably-invalid-package-name')

    def test_get_homepage(self):
        out = self.frontend._get_homepage({})
        self.assertIsNone(out)

        out = self.frontend._get_homepage({'homepage': 'foo'})
        self.assertEqual(out, 'foo')

        out = self.frontend._get_homepage({'bugtracker': {'web': 'foo'}})
        self.assertEqual(out, 'foo')

        out = self.frontend._get_homepage({'repository': {'web': 'foo'}})
        self.assertEqual(out, 'foo')

        json = {'repository': {'web': 'bar'}, 'homepage': 'foo'}
        out = self.frontend._get_homepage(json)
        self.assertEqual(out, 'foo')


class TestCPANJson(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()
        self.url = 'https://fastapi.metacpan.org/v1/release/perl-foo'

    @requests_mock.mock()
    def test_missing_metadata(self, requests):
        requests.get(self.url, json={})
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.version, '')
        self.assertEqual(pkg.summary, '')

    @requests_mock.mock()
    def test_missing_version(self, requests):
        json = {
            'metadata': {
                'abstract': 'foo bar baz'
            }
        }
        requests.get(self.url, json=json)
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.version, '')

    @requests_mock.mock()
    def test_missing_abstract(self, requests):
        json = {
            'metadata': {
                'version': '13.37'
            }
        }
        requests.get(self.url, json=json)
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.summary, '')

    @requests_mock.mock()
    def test_missing_license(self, requests):
        requests.get(self.url, json={})
        pkg = self.frontend.parse('perl-foo')
        self.assertEqual(pkg.licenses, [])

    @requests_mock.mock()
    def test_download_urls(self, requests):
        requests.get(self.url, json={})
        pkg = self.frontend.parse('perl-foo')
        self.assertListEqual(pkg.download_urls, [])

        requests.get(self.url, json={'download_url': 'foo'})
        pkg = self.frontend.parse('perl-foo')
        self.assertListEqual(pkg.download_urls, ['foo'])


class TestLicenses(unittest.TestCase):
    def setUp(self):
        self.frontend = CPANFrontend()

    def test_no_licenses(self):
        self.assertEqual(self.frontend._get_licenses([]), [])

    def test_one_license(self):
        out = self.frontend._get_licenses(['bsd'])
        expected = [upt.licenses.BSDThreeClauseLicense()]
        self.assertListEqual(out, expected)

        out = self.frontend._get_licenses(['whatever'])
        expected = [upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)

    def test_multiple_licenses(self):
        out = self.frontend._get_licenses(['freebsd', 'whatever'])
        expected = [upt.licenses.BSDTwoClauseLicense(),
                    upt.licenses.UnknownLicense()]
        self.assertListEqual(out, expected)


if __name__ == '__main__':
    unittest.main()
