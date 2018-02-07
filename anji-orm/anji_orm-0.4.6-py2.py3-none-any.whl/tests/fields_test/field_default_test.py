import unittest

from anji_orm import StringField, Model


class T1(Model):

    _table = 'non_table'

    c1 = StringField(default='5')


class FieldValidationTest(unittest.TestCase):

    def test_simple_default(self) -> None:
        test_record = T1()
        self.assertEqual(test_record.c1, '5')
