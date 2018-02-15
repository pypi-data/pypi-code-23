import unittest
from ..schema import SchemaBase

class BookSchema(SchemaBase):

    TABLE_NAME = 'books'

    FIELDS = ('id', 'name', 'author_id')

    PRIMARY_KEY_FIELDS = ('id',)


class AuthorSchema(SchemaBase):

    TABLE_NAME = 'authors'

    FIELDS = ('id', 'name')

    PRIMARY_KEY_FIELDS = ('id',)


class TestSelectSQLJoin(unittest.TestCase):

    def test_before_join(self):
        sql = BookSchema.create_select_sql()
        self.assertEqual(str(sql), 'SELECT * FROM books')
        self.assertEqual(sql.data, ())


    def test_join(self):
        sql = BookSchema.create_select_sql()

        author_sql = AuthorSchema.create_join_sql()

        sql.add_join(author_sql, 'INNER JOIN', (sql.field('author_id'),
                author_sql.field('id'), '='))

        self.assertEqual(str(author_sql), 'INNER JOIN authors ON ' +\
                'books.author_id = authors.id')
        self.assertEqual(author_sql.data, ())

        self.assertEqual(str(sql), 'SELECT * FROM books INNER JOIN authors ' +\
                'ON books.author_id = authors.id')


    def test_join_with_filters(self):
        sql = BookSchema.create_select_sql()
        sql.set_filters(('id', 23, '='))

        author_sql = AuthorSchema.create_join_sql()
        author_sql.set_filters(('name', 'Bro%', 'LIKE'))

        sql.add_join(author_sql, 'INNER JOIN', (sql.field('author_id'),
                author_sql.field('id'), '='))

        self.assertEqual(str(author_sql), 'INNER JOIN authors ON ' +\
                'books.author_id = authors.id')
        self.assertEqual(author_sql.data, ())

        self.assertEqual(str(sql), 'SELECT * FROM books INNER JOIN authors ' +\
                'ON books.author_id = authors.id WHERE books.id = %s AND ' +\
                'authors.name LIKE %s')
