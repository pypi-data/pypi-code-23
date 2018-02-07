import unittest

from anji_orm.model import fetch

from .base_models import BaseModel


class FetchTest(unittest.TestCase):

    def test_base_fetch(self):
        base_record = BaseModel(test_field_1='5', test_field_2='8')
        fetch_dict = base_record.to_dict()
        fetch_dict['id'] = '55'
        self.assertEqual(
            base_record.to_dict(),
            fetch(fetch_dict).to_dict()
        )

    def test_fetch_dict(self):
        some_dict = {5: 6, 7: 8}
        self.assertEqual(some_dict, fetch(some_dict))
