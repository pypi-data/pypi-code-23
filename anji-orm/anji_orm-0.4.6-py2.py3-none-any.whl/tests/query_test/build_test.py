import rethinkdb as R

from anji_orm.model import Model
from anji_orm.fields import StringField
from anji_orm.syntax.parse import RethinkDBQueryParser

from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = StringField()
    c4 = StringField(secondary_index=True)


class BaseQuerySecondaryIndexTest(BaseTestCase):

    def test_simple_build(self):
        self.assertQueryEqual(
            R.table('non_table').get_all('a1', 'a2', index='c2'),
            RethinkDBQueryParser.build_query(T1, T1.c2.one_of('a1', 'a2'))
        )

        self.assertQueryEqual(
            R.table('non_table').get_all('a1', index='c2'),
            RethinkDBQueryParser.build_query(T1, T1.c2 == 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').between('a1', R.maxval, index='c2', left_bound='open', right_bound='open'),
            RethinkDBQueryParser.build_query(T1, T1.c2 > 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').between('a1', R.maxval, index='c2', left_bound='closed', right_bound='open'),
            RethinkDBQueryParser.build_query(T1, T1.c2 >= 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').between(R.minval, 'a1', index='c2', left_bound='open', right_bound='open'),
            RethinkDBQueryParser.build_query(T1, T1.c2 < 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').between(R.minval, 'a1', index='c2', left_bound='open', right_bound='closed'),
            RethinkDBQueryParser.build_query(T1, T1.c2 <= 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').between(5, 10, index='c2', left_bound='closed', right_bound='closed'),
            RethinkDBQueryParser.build_query(T1, (T1.c2 <= 10) & (T1.c2 >= 5))
        )

        self.assertQueryEqual(
            R.table('non_table').between(5, 10, index='c2', left_bound='closed', right_bound='open'),
            RethinkDBQueryParser.build_query(T1, (T1.c2 < 10) & (T1.c2 >= 5))
        )

        self.assertQueryEqual(
            R.table('non_table').between(5, 10, index='c2', left_bound='open', right_bound='closed'),
            RethinkDBQueryParser.build_query(T1, (T1.c2 <= 10) & (T1.c2 > 5))
        )

        self.assertQueryEqual(
            R.table('non_table').between(5, 10, index='c2', left_bound='open', right_bound='open'),
            RethinkDBQueryParser.build_query(T1, (T1.c2 < 10) & (T1.c2 > 5))
        )

    def test_compound_index_build(self):
        self.assertQueryEqual(
            R.table('non_table').get_all(['t1', 't2'], index='c1:c2'),
            RethinkDBQueryParser.build_query(T1, (T1.c1 == 't1') & (T1.c2 == 't2'))
        )

    def complicated_contains_build(self):
        self.assertQueryEqual(
            R.table('non_table').filter(lambda doc: doc['c1'].contains('5')),
            RethinkDBQueryParser.build_query(T1, T1.c1.contains('5'))
        )

        self.assertQueryEqual(
            R.table('non_table').filter(lambda doc: doc['c1'].contains(doc['c2'])),
            RethinkDBQueryParser.build_query(T1, T1.c1.contains(T1.c2))
        )

    def test_with_not_index_build(self):

        self.assertQueryEqual(
            R.table('non_table').get_all('a1', 'a2', index='c2').filter(R.row['c3'] < 5),
            RethinkDBQueryParser.build_query(T1, (T1.c2.one_of('a1', 'a2')) & (T1.c3 < 5))
        )


class BaseQuerySimpleFieldsTest(BaseTestCase):

    def test_simple_build(self):
        rethinkdb_list = R.expr(['a1', 'a2'])
        row = R.row['c3']

        self.assertQueryEqual(
            R.table('non_table').filter(lambda doc: rethinkdb_list.contains(doc['c3'])),
            RethinkDBQueryParser.build_query(T1, T1.c3.one_of('a1', 'a2'))
        )

        self.assertQueryEqual(
            R.table('non_table').filter(row == 'a1'),
            RethinkDBQueryParser.build_query(T1, T1.c3 == 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').filter(row > 'a1'),
            RethinkDBQueryParser.build_query(T1, T1.c3 > 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').filter(row >= 'a1'),
            RethinkDBQueryParser.build_query(T1, T1.c3 >= 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').filter(row < 'a1'),
            RethinkDBQueryParser.build_query(T1, T1.c3 < 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').filter(row <= 'a1'),
            RethinkDBQueryParser.build_query(T1, T1.c3 <= 'a1')
        )

        self.assertQueryEqual(
            R.table('non_table').filter((row <= 10) & (row >= 5)),
            RethinkDBQueryParser.build_query(T1, (T1.c3 <= 10) & (T1.c3 >= 5))
        )

        self.assertQueryEqual(
            R.table('non_table').filter((row < 10) & (row >= 5)),
            RethinkDBQueryParser.build_query(T1, (T1.c3 < 10) & (T1.c3 >= 5))
        )

        self.assertQueryEqual(
            R.table('non_table').filter((row <= 10) & (row > 5)),
            RethinkDBQueryParser.build_query(T1, (T1.c3 <= 10) & (T1.c3 > 5))
        )

        self.assertQueryEqual(
            R.table('non_table').filter((row < 10) & (row > 5)),
            RethinkDBQueryParser.build_query(T1, (T1.c3 < 10) & (T1.c3 > 5))
        )
