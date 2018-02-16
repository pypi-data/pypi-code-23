# -*- coding: utf-8; -*-

from __future__ import unicode_literals, absolute_import

import decimal

import six

from rattail.db import model
from rattail.tests import DataTestCase


class TestDepartment(DataTestCase):

    def test_unicode(self):
        dept = model.Department()
        self.assertEqual(six.text_type(dept), "")

        dept = model.Department(name=b"Grocery")
        self.assertEqual(six.text_type(dept), "Grocery")


class TestSubdepartment(DataTestCase):

    def test_unicode(self):
        subdept = model.Subdepartment()
        self.assertEqual(six.text_type(subdept), "")

        subdept = model.Subdepartment(name=b"Canned Goods")
        self.assertEqual(six.text_type(subdept), "Canned Goods")


class TestCategory(DataTestCase):

    def test_unicode(self):
        category = model.Category()
        self.assertEqual(six.text_type(category), "")

        category = model.Category(name=b"Various Odds and Ends")
        self.assertEqual(six.text_type(category), "Various Odds and Ends")


class TestFamily(DataTestCase):

    def test_unicode(self):
        family = model.Family()
        self.assertEqual(six.text_type(family), "")

        family = model.Family(name=b"Various Odds and Ends")
        self.assertEqual(six.text_type(family), "Various Odds and Ends")


class TestReportCode(DataTestCase):

    def test_unicode(self):
        code = model.ReportCode()
        self.assertEqual(six.text_type(code), "")

        code = model.ReportCode(code=42, name=b"Various Odds and Ends")
        self.assertEqual(six.text_type(code), "42 - Various Odds and Ends")
