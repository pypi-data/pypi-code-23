from unittest import TestCase

from slerp import (is_json, is_empty, is_blank, is_email, is_not_empty, is_palindrome, get_name_abbreviations, \
	random_colors)


class TestString(TestCase):
	
	def setUp(self):
		pass
	
	def is_json(self):
		self.assertEqual(is_json('{"key":"value"}'), True)
		self.assertEqual(is_json('ERROR'), False)
		self.assertEqual(is_json(False), False)

	def test_email(self):
		self.assertEqual(is_email('kiditzbastara@gmail.com'), True)
		self.assertEqual(is_email('kiditzbastaragmail.com'), False)
		self.assertEqual(is_email('kiditzbastara@gmail'), False)

	def test_blank(self):
		self.assertEqual(is_blank('        '), True)
		self.assertEqual(is_blank(' '), True)
		self.assertEqual(is_blank(''), True)
		self.assertEqual(is_blank('TEST'), False)

	def test_empty(self):
		self.assertEqual(is_empty(''), True)
		self.assertEqual(is_empty(' '), False)
		self.assertEqual(is_empty('empty'), False)

	def test_not_empty(self):
		self.assertEqual(is_not_empty('  '), True)
		self.assertEqual(is_not_empty(''), False)
		self.assertEqual(is_not_empty('empty'), True)

	def test_palindrome(self):
		self.assertEqual(is_palindrome('TAMAT'), True)
		self.assertEqual(is_palindrome('Tamat'), False)
		self.assertEqual(is_palindrome('Pisang'), False)

	def test_random_color(self):
		color = random_colors(use_hastag=True)
		self.assertEqual(color.startswith('#'), True)
		color = random_colors()
		self.assertEqual(color.startswith('#'), False)

	def test_get_simple_name(self):
		self.assertEqual(get_name_abbreviations('rifky aditya bastara'), 'RAB')
		self.assertEqual(get_name_abbreviations('hidayanti anatya bastari jelek'), 'HAB')
		self.assertEqual(get_name_abbreviations('hidayanti anatya'), 'HA')
		self.assertEqual(get_name_abbreviations('hidayanti anatya bastari jelek banget'), 'HAB')