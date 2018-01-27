import rethinkdb as R

from .base_models import BaseModel
from ..base import BaseTestCase


class OrmFeatureTest(BaseTestCase):

    def test_all(self):
        self.assertQueryEqual(
            BaseModel.all(),
            R.table(BaseModel._table)
        )

        self.assertQueryEqual(
            BaseModel.all(limit=5),
            R.table(BaseModel._table).limit(5)
        )

        self.assertQueryEqual(
            BaseModel.all(skip=5),
            R.table(BaseModel._table).skip(5)
        )

        self.assertQueryEqual(
            BaseModel.all(limit=5, skip=6),
            R.table(BaseModel._table).skip(6).limit(5)
        )

    def test_count(self):
        self.assertQueryEqual(
            BaseModel.count(),
            R.table(BaseModel._table).count()
        )

        self.assertQueryEqual(
            BaseModel.count(BaseModel.test_field_1 == '5'),
            R.table(BaseModel._table).filter(R.row['test_field_1'] == '5').count()
        )

    def test_sample(self):
        self.assertQueryEqual(
            BaseModel.sample(5),
            R.table(BaseModel._table).sample(5)
        )

        self.assertQueryEqual(
            BaseModel.sample(5, BaseModel.test_field_1 == '5'),
            R.table(BaseModel._table).filter(R.row['test_field_1'] == '5').sample(5)
        )

    def test_similarity_query(self):
        python_info_dict = {'module_name': 'tests.models_test.base_models', 'class_name': 'BaseModel'}
        test_record = BaseModel(test_field_3='5')
        self.assertAstEqual(
            (BaseModel.test_field_3 == '5') & (BaseModel._python_info == python_info_dict),
            test_record.build_similarity_query()
        )

        self.assertQueryEqual(
            R.table(BaseModel._table).get_all('5', index='test_field_3').filter(R.row['_python_info'] == python_info_dict),
            test_record.db_query(test_record.build_similarity_query())
        )
