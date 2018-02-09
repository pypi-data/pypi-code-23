# -*- coding: utf8 -*-
import six

from .luqum.tree import OrOperation, Word, Item, Phrase
from .luqum.utils import LuceneTreeVisitorV2, UnknownOperationResolver, LuceneTreeTransformer
from .luqum.parser import parser, lexer, ParseError
import pyparsing as pp


def process_vals(t, l):
    res = []
    for val in t:
        res.append(l(val))

    return res


def convert_number(t):
    def int_or_float(val):
        if '.' in val:
            return float(val)

        return int(val)

    return process_vals(t, int_or_float)


def parse_expr(expr_text):
    operator = pp.Regex(">=|<=|!=|>|<|=")('operator')

    point = pp.Literal('.')
    e = pp.CaselessLiteral('E')
    plus_or_minus = pp.Literal('+') | pp.Literal('-')
    number = pp.Word(pp.nums)
    integer = pp.Combine(pp.Optional(plus_or_minus) + number)
    float_number = pp.Combine(integer + pp.Optional(point + pp.Optional(number)) + pp.Optional(e + integer) + pp.stringEnd)

    float_number.setParseAction(convert_number)

    identifier = ~float_number + pp.Word(pp.alphanums + "_" + "." + "-")

    quoted_string = pp.QuotedString('"')
    text_identifier = (quoted_string | identifier)
    comparison_term = text_identifier | float_number
    values = pp.OneOrMore(comparison_term)('values')
    range_op = pp.Suppress(pp.CaselessLiteral('TO'))
    range_operator = (pp.Suppress('[') + comparison_term + range_op + comparison_term + pp.Suppress(']'))('range')
    range_inclusive = (pp.Suppress('{') + comparison_term + range_op + comparison_term + pp.Suppress('}'))('range_inclusive')

    condition_group = pp.Group((range_inclusive | range_operator | values | (operator + values)))('condition_group')
    conditions = pp.Group(condition_group)('conditions')

    expr = pp.infixNotation(conditions, [
        ("AND", 2, pp.opAssoc.LEFT,),
        ("OR", 2, pp.opAssoc.LEFT,),
    ])

    return expr.parseString(expr_text)


def __conditions_expr_to_sql_where(field_name, item):
    return '({sql})'.format(sql=expr_to_sql_where(field_name, item))


def quotes_if_needed(val):
    return '"%s"' % val if isinstance(val, six.string_types) else val


def __condition_group_expr_to_sql_where(field_name, item):
    if 'values' in item:
        values = item.get('values')
        operator = item.get('operator', '=')
        vals = []
        for val in values:
            vals.append('`{field_name}`{operator}{value}'.format(
                field_name=field_name, operator=operator, value=quotes_if_needed(val)))

        return 'OR'.join(vals)

    if 'range' in item:
        return ('(`{field_name}`>={value1})AND(`{field_name}`<={value2})'.format(
            field_name=field_name, value1=item[0], value2=item[1]))

    if 'range_inclusive' in item:
        return ('(`{field_name}`>{value1})AND(`{field_name}`<{value2})'.format(
            field_name=field_name, value1=item[0], value2=item[1]))


def expr_to_sql_where(field_name, expr):
    sql = ''
    for item in expr:
        if item.getName() == 'conditions':
            sql += __conditions_expr_to_sql_where(field_name, item)
        elif item.getName() == 'condition_group':
            sql += __condition_group_expr_to_sql_where(field_name, item)

    return sql


class QueryFunction(Item):
    def __init__(self, name, node):
        self.name = name
        self.node = node

    def __str__(self):
        return str(self.node)


class FunctionVersion(QueryFunction):
    def __init__(self, name, node):
        super(FunctionVersion, self).__init__(name, node)
        self.version = str(node.expr)


class FunctionSplit(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSplit, self).__init__(name, node)

        self.split_field = None
        self.split = {}

        split_vars = self.__validate_split_params(node)

        try:
            split_vars = list(map(float, split_vars))
            split_vars += [None] * (3 - len(split_vars))

            self.split = dict(zip(('train', 'test', 'validation'), split_vars))
        except ValueError:
            if len(split_vars) == 1:
                self.split_field = split_vars[0]
            else:
                raise ParseError('invalid values in @split')

    @classmethod
    def __validate_split_params(cls, node):
        split_vars = str(node)
        split_vars = split_vars.split(':')

        if len(split_vars) > 4:
            raise ParseError('too many values in @split')

        if len(split_vars) == 1:
            raise ParseError('@split needs at least one value')

        return split_vars[1:]


class FunctionSample(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSample, self).__init__(name, node)
        self.sample = float(node.expr.value)


class FunctionSeed(QueryFunction):
    def __init__(self, name, node):
        super(FunctionSeed, self).__init__(name, node)
        self.seed = int(str(node.expr))


class FunctionGroup(QueryFunction):
    def __init__(self, name, node):
        super(FunctionGroup, self).__init__(name, node)
        self.group = str(node.expr)


class FunctionLimit(QueryFunction):
    def __init__(self, name, node):
        super(FunctionLimit, self).__init__(name, node)
        self.limit = int(str(node.expr))


class MLQueryMixin(object):
    @classmethod
    def _handle_internal_function(cls, node):
        if node.name.startswith('@'):
            func_name = node.name[1:]
            func_class_name = 'Function%s' % func_name.title()

            function_class = globals().get(func_class_name)

            return function_class(func_name, node)

        return None


# noinspection PyClassicStyleClass
class MLQueryTransformer(LuceneTreeTransformer, MLQueryMixin):
    def visit_search_field(self, node, parents):
        return self._handle_internal_function(node) or node

    def __call__(self, tree):
        return self.visit(tree)


class MLQueryVisitor(LuceneTreeVisitorV2):
    def __visit_binary_operation(self, node, parents, context, op):
        context = context or {}
        context['op'] = op
        for child in node.children:
            self.visit(child, context=context)

    def visit_and_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'AND')

    def visit_or_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'OR')


# noinspection PyClassicStyleClass
class SQLQueryBuilder(MLQueryVisitor, MLQueryMixin):
    def __init__(self, sql_helper):
        self.__where = {}
        self.__limit = []
        self.__vars = {}
        self.__sql_helper = sql_helper

    internal_function_names = ['sample', 'seed', 'group', 'version', 'limit']

    def visit_function_sample(self, node, parents=None, context=None):
        sample_percentile = 1.0 - node.sample

        self.__where.setdefault(1, []).append(
            ('AND', '($random_function>{sample_percentile:.4g})'.format(sample_percentile=sample_percentile)))
        self.__vars['sample_percentile'] = sample_percentile
        self.__vars['sample'] = node.sample

    def visit_function_seed(self, node, parents=None, context=None):
        self.__vars['seed'] = node.seed

    def visit_function_group(self, node, parents=None, context=None):
        self.__vars['group'] = node.group

    def visit_function_split(self, node, parents=None, context=None):
        if node.split_field is not None:
            self.__vars['split_field'] = node.split_field
        else:
            self.__vars.update(get_split_vars(node.split))

    def visit_function_version(self, node, parents=None, context=None):
        self.__vars['version'] = node.version

    def visit_func_limit(self, node, parents=None, context=None):
        self.__vars['limit'] = node.limit

    def visit_group(self, node, parents=None, context=None):
        self._sub_visit(node.expr, None, is_group=True)

    def visit_prohibit(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_phrase(self, node, parents=None, context=None):
        phrase = str(node)

        phrase = phrase.strip()

        self.__add_where(context.get('field_name'), phrase, context.get('op'))

    def visit_range(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_plus(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node)[1:], context.get('op'))

    def visit_field_group(self, node, parents=None, context=None):
        self.visit(node.expr, parents + [node], context)

    def __add_where(self, field_name, expr, op):
        if expr is None:
            self.__where.setdefault(0, []).append((None, '%s is NULL' % field_name))
            return

        where = expr_to_sql_where(field_name, parse_expr(expr))
        self.__where.setdefault(0, []).append((op, where))

    def visit_word(self, node, parents=None, context=None):
        if context is None:
            raise ParseError('invalid field %s' % node)

        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    def visit_search_field(self, node, parents=None, context=None):
        function_node = self._handle_internal_function(node)
        if function_node is not None:
            return function_node

        context = context or {}

        for child in node.children:
            if isinstance(child, (Word, Phrase)):
                value = str(node.expr)
                if value.lower() == 'null':
                    self.__add_where(node.name, None, 'is')
                else:
                    self.__add_where(node.name, value, context.get('op'))
            else:
                sub_context = {}
                sub_context.update(context)
                sub_context['field_name'] = node.name
                self._sub_visit(node.expr, None, context=sub_context)

    @classmethod
    def __combine_where(cls, op, sql_builder):
        combine_where = {}
        for bucket, wheres in sorted(sql_builder.where.items()):
            for where in wheres:
                operator, expr = where
                operator = operator or op

                combine_where.setdefault(bucket, []).append((operator, expr))

        return combine_where

    def _sub_visit(self, child, op, context=None, is_group=False):
        sql_builder = SQLQueryBuilder(self.__sql_helper)
        sql_builder.visit(child, context=context)

        self.__vars.update(sql_builder.vars)

        combine_where = self.__combine_where(op, sql_builder)

        for bucket, wheres in combine_where.items():
            op = None
            sql = ''
            for where in wheres:
                operator, expr = where
                if op is not None:
                    sql += op

                sql += expr
                op = operator

            if len(wheres) > 1 or is_group:
                sql = self.wrap_in_parentheses(sql)

            self.__where.setdefault(bucket, []).append((None, sql))

    @classmethod
    def wrap_in_parentheses(cls, text):
        return '(%s)' % text

    def build_vars(self):
        if not self.__vars:
            return None

        return self.__vars

    def __build_where(self):
        sql = ''
        for bucket, wheres in sorted(self.__where.items()):
            last_operator = None

            for where in wheres:
                operator, expr = where

                if last_operator:
                    sql += last_operator
                elif sql:
                    sql += operator

                sql += expr

                last_operator = operator

        return sql

    def build_where(self):
        return self.__build_where() or None  # Make sure to return None and not empty string

    @property
    def where(self):
        return self.__where

    @property
    def vars(self):
        return self.__vars


def get_split_vars(split):
    sql_vars = {}

    start = 0.
    for phase in ['train', 'test', 'validation']:
        percentage = split.get(phase)
        if phase is None:
            continue

        if percentage is None:
            sql_vars['phase_%s_start' % phase] = -1
            sql_vars['phase_%s_end' % phase] = -1
            continue

        sql_vars['phase_%s_start' % phase] = start
        sql_vars['phase_%s_end' % phase] = start + percentage

        start += percentage

    return sql_vars


class QueryParser(object):
    def __init__(self):
        self.__parser = parser()

    def parse_query(self, query):
        return self.__parser.parse(query, lexer=lexer())


def resolve_tree(tree, *transformers):
    resolver = UnknownOperationResolver(OrOperation)
    resolved_tree = resolver(tree)

    transformers2 = [MLQueryTransformer()]

    transformers2.extend(transformers)

    for transformer in transformers2:
        resolved_tree = transformer(resolved_tree)

    return resolved_tree


def visit_query(visitor, tree):
    resolver = resolve_tree(tree)
    visitor.visit(resolver)

    return visitor


def tree_to_sql_parts(tree, sql_helper):
    sql_builder = SQLQueryBuilder(sql_helper)
    visit_query(sql_builder, tree)

    return sql_builder.build_vars(), sql_builder.build_where()


if __name__ == '__main__':  # pragma: no cover
    QueryParser().parse_query('@version:a196d73071e57874768e20267a1bec4ed0a8c2b7')
