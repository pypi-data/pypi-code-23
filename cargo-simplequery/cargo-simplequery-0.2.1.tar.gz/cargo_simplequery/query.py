import psycopg2
import psycopg2.sql as sql


class SelectQueryBuilder:
    def __init__(self, table, columns: list):
        self.cols = columns
        self.table = table
        self.whereClause = None
        self.joins = []
        self._combinator = sql.SQL('AND')
        self._limit = sql.SQL('')
        self._order_by = []
        self.group_by = sql.SQL('')

    def where(self):
        if self.whereClause is None:
            self.whereClause = WhereClause()
        return self.whereClause

    def inner_join(self, table):
        clause = InnerJoinClause(table)
        self.joins.append(clause)
        return clause

    def left_join(self, table):
        clause = LeftJoinClause(table)
        self.joins.append(clause)
        return clause

    def set_group_by(self, group_clause: sql.SQL):
        self.group_by = sql.SQL("\n") + group_clause

    def set_page(self, items: int, page: int):
        self._limit = sql.SQL("\nLIMIT {} OFFSET {}").format(sql.Literal(items), sql.Literal(items * (page - 1)))

    def limit(self, limit: int, offset: int):
        self._limit = sql.SQL("\nLIMIT {} OFFSET {}").format(sql.Literal(limit), sql.Literal(offset))

    def order_by(self, column, order):
        ordering = sql.SQL('ASC')
        if order.upper() == 'DESC':
            ordering = sql.SQL('DESC')
        self._order_by.append(sql.SQL('{} {}').format(wrap_identifier(column), ordering))

    def get_query(self):
        select = sql.SQL('SELECT {} FROM {}').format(
            sql.SQL(', ').join([wrap_identifier(x) for x in self.cols]),
            wrap_identifier(self.table)
        )
        if len(self.joins) > 0:
            select += sql.SQL("\n") + sql.SQL("\n").join([j.get_query() for j in self.joins])
        if self.whereClause is not None:
            select += sql.SQL("\nWHERE {}").format(self.whereClause.get_query())
        select += self.group_by
        if len(self._order_by) > 0:
            select += sql.SQL("\nORDER BY {}").format(sql.SQL(', ').join(self._order_by))
        select += self._limit
        return select


class WhereClause:
    def __init__(self):
        """

        :rtype: WhereClause
        """
        self._clauses = []

    def in_(self, field, *args):
        if len(args) == 0:
            raise ArgumentExpectedException()
        self._auto_combinator_check()
        if isinstance(args[0], list):
            self._clauses.append(sql.SQL('{} IN ({})').format(
                wrap_identifier(field),
                sql.SQL(', ').join([sql.Literal(x) for x in args[0]]))
            )
        else:
            self._clauses.append(sql.SQL('{} IN ({})').format(
                wrap_identifier(field),
                sql.SQL(', ').join([sql.Literal(x) for x in args]))
            )
        return self

    def eq(self, field, value):
        self._auto_combinator_check()
        self._clauses.append(sql.SQL('{} = {}').format(wrap_identifier(field), wrap_literal(value)))
        return self

    def like(self, field, value):
        self._auto_combinator_check()
        self._clauses.append(sql.SQL('{} LIKE {}').format(wrap_identifier(field), wrap_literal(value)))
        return self

    def or_(self):
        self._clauses.append(Combinator().or_())
        return self

    def and_(self):
        self._clauses.append(Combinator())
        return self

    def sub(self):
        self._auto_combinator_check()
        w = WhereClause()
        self._clauses.append(w)
        return w

    def get_query(self):
        clauses = []
        for c in self._clauses:
            if isinstance(c, Combinator):
                clauses.append(c.get_query())
            elif isinstance(c, WhereClause):
                clauses.append(c.get_query())
            else:
                clauses.append(c)
        return sql.SQL('({})').format(sql.SQL(' ').join(clauses))

    def _auto_combinator_check(self):
        length = len(self._clauses)
        if length == 0:
            return
        last_element = self._clauses[length-1]
        if not isinstance(last_element, Combinator):
            self._clauses.append(Combinator())


class Combinator():
    def __init__(self):
        self.type = sql.SQL(' AND ')

    def or_(self):
        self.type = sql.SQL(' OR ')
        return self

    def and_(self):
        self.type = sql.SQL(' AND ')
        return self

    def get_query(self):
        return self.type

class JoinClause:
    def __init__(self, table):
        self.table = table
        self.on = []

    def on_eq(self, first, second):
        self.on.append(sql.SQL('{} = {}').format(wrap_identifier(first), wrap_identifier(second)))
        return self

    def get_query(self):
        q = sql.SQL(self._get_join_template()).format(wrap_identifier(self.table))
        if len(self.on) > 0:
            q += sql.SQL(' ON ') + sql.SQL(' AND ').join(self.on)
        return q

    def _get_join_template(self):
        return 'JOIN {}'


class InnerJoinClause(JoinClause):
    def _get_join_template(self):
        return 'INNER JOIN {}'


class LeftJoinClause(JoinClause):
    def _get_join_template(self):
        return 'LEFT JOIN {}'


class InsertQueryBuilder():
    def __init__(self, table, columns):
        self.table = table
        self.cols = columns

    def add_column(self, column):
        self.cols.append(column)

    def execute(self, cursor, values, returning=None):
        q = self.get_query()
        if returning:
            q += sql.SQL(' RETURNING {}').format(sql.Identifier(returning))
        cursor.execute(q, values)
        if returning:
            return cursor.fetchone()[0]
        return None

    def get_query(self):
        return sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
            sql.Identifier(self.table),
            sql.SQL(', ').join([sql.Identifier(x) for x in self.cols]),
            sql.SQL(', ').join(sql.Placeholder() * len(self.cols))
        )


class MultiInsertQueryBuilder():
    def __init__(self, table, columns):
        self.table = table
        self.cols = columns

    def add_column(self, column):
        self.cols.append(column)

    def execute(self, cursor, values):
        q = self.get_query(len(values))
        cursor.execute(q, tuple(value for tupleValues in values for value in tupleValues))
        return None

    def get_query(self, amount):
        return sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
            sql.Identifier(self.table),
            sql.SQL(', ').join([sql.Identifier(x) for x in self.cols]),
            sql.SQL('), (').join([sql.SQL(', ').join(sql.Placeholder() * len(self.cols)) for i in range(amount)])
        )


class UpdateQueryBuilder():
    def __init__(self, table, columns):
        self.table = table
        self.cols = columns
        self.whereClause = None
        self._limit = sql.SQL('')

    def add_column(self, column):
        self.cols.append(column)

    def where(self):
        if self.whereClause is None:
            self.whereClause = WhereClause()
        return self.whereClause

    def execute(self, cursor, values):
        cursor.execute(self.get_query(), values)
        return cursor.rowcount

    def limit(self, limit):
        self._limit = sql.SQL("\nLIMIT {}").format(sql.Literal(limit))

    def get_query(self):
        return sql.SQL('UPDATE {} SET {} WHERE {} {}').format(
            sql.Identifier(self.table),
            sql.SQL(', ').join([sql.SQL('{} = {}').format(sql.Identifier(c), sql.Placeholder()) for c in self.cols]),
            self.whereClause.get_query(),
            self._limit
        )


class DeleteQueryBuilder():
    def __init__(self, table):
        self.table = table
        self.whereClause = None

    def where(self):
        if self.whereClause is None:
            self.whereClause = WhereClause()
        return self.whereClause

    def execute(self, cursor):
        cursor.execute(self.get_query())
        return cursor.rowcount

    def get_query(self):
        return sql.SQL('DELETE FROM {} WHERE {}').format(
            sql.Identifier(self.table),
            self.whereClause.get_query()
        )


class ArgumentExpectedException(BaseException):
    pass


def wrap_identifier(input):
    if isinstance(input, sql.Literal):
        return input
    if isinstance(input, sql.Identifier):
        return input
    if isinstance(input, sql.SQL):
        return input
    if isinstance(input, sql.Composed):
        return input
    if input == '*':
        return sql.SQL(input)
    if input.find(' ') != -1:
        parts = input.split(' ', maxsplit=1)
        return sql.SQL('{} AS {}').format(sql.Identifier(parts[0]), sql.Identifier(parts[1]))
    if input.find('.') != -1:
        return sql.SQL('.').join([sql.Identifier(x) for x in input.split('.', maxsplit=1)])
    if input.find('::') != -1:
        return sql.SQL('::').join([sql.Identifier(x) for x in input.split('::', maxsplit=1)])
    return sql.Identifier(input)


def wrap_literal(input):
    if isinstance(input, sql.SQL):
        return input
    return sql.Literal(input)
