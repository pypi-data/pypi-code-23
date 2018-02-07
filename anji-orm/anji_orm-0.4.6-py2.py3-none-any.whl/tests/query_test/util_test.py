from enum import Enum
import unittest

from anji_orm.model import Model
from anji_orm.fields import StringField, EnumField


class NotPrettyEnum(Enum):

    first = 'first'
    second = 'second'


class T1(Model):

    _table = 'non_table'

    c1 = StringField()
    c2 = StringField()
    c3 = EnumField(NotPrettyEnum)


class QueryUtilTest(unittest.TestCase):

    def test_check_complicated(self):
        self.assertTrue((T1.c1 == T1.c2).complicated)
        self.assertFalse((T1.c1 == '5').complicated)
        self.assertFalse(((T1.c1 == '5') & (T1.c1 == '6')).complicated)
        self.assertTrue(((T1.c1 == '5') & (T1.c2 == '6')).complicated)
        self.assertTrue(((T1.c1 == T1.c2) & (T1.c2 == '6')).complicated)
        self.assertTrue(((T1.c1 == T1.c2) & (T1.c1 == '6')).complicated)

    def test_check_prettify_for_enum(self):
        self.assertEqual(
            (NotPrettyEnum.first.name, NotPrettyEnum.second.name),
            T1.c1.one_of(NotPrettyEnum.first, NotPrettyEnum.second).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 == NotPrettyEnum.first).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 >= NotPrettyEnum.first).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 <= NotPrettyEnum.first).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 > NotPrettyEnum.first).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 < NotPrettyEnum.first).right
        )

        self.assertEqual(
            NotPrettyEnum.first.name,
            (T1.c1 != NotPrettyEnum.first).right
        )
