import unittest

from jsonschema import ValidationError

from anji_orm import ValidableJsonField, Model


class T1(Model):

    _table = 'non_table'

    c1 = ValidableJsonField({
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "name": {"type": "string"},
        }
    })


class FieldValidationTest(unittest.TestCase):

    def test_validation(self) -> None:
        test_record = T1()
        with self.assertRaises(ValidationError) as _cm:
            test_record.c1 = {'price': 5, 'name': 6}
        good_value = {'price': 5, 'name': 't1'}
        test_record.c1 = good_value
        self.assertEqual(good_value, test_record.c1)
        with self.assertRaises(ValueError) as _cm:
            test_record.c1 = 5
