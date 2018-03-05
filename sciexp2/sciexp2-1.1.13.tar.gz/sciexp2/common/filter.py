#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parse and apply filter expressions."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import abc
import ply.lex as lex
import ply.yacc as yacc
import re
import six
import sys

from . import utils


class ParseError (AssertionError):
    """Exception signaling parse errors."""
    pass


class FilterError (Exception):
    """Exception signaling a filter with an unknown variable name."""

    def __init__(self, name, filter_):
        Exception.__init__(self, name, Filter(filter_))

    def __str__(self):
        return "Unknown variable '%s' in filter: %s" % (
            repr(self.args[0]), repr(str(self.args[1])))


class FilterExprError (Exception):
    """Exception signaling an unknown error during expression evaluation."""

    def __init__(self, expression, e):
        Exception.__init__(self, expression, e)

    def __str__(self):
        return "Error evaluating expression: %s\n  [was] %s: %s" %\
            (self.args[0],
             self.args[1].__class__.__name__,
             self.args[1])


class FilterEvalError (Exception):
    """Exception signaling an unknown error during filter evaluation."""

    def __init__(self, filter_, instance, e):
        Exception.__init__(self, filter_, instance, e)

    def __str__(self):
        return "Error evaluating filter '%s' with: %r\n  [was] %s: %s" %\
            (self.args[0], self.args[1],
             self.args[2].__class__.__name__,
             self.args[2])


class FilterUnallowedError (Exception):
    """Exception signaling a filter with an unallowed variable name."""

    def __init__(self, name, filter_):
        Exception.__init__(self, name, filter_)

    def __str__(self):
        return "Unallowed variable %r in filter: %s" % (self.args[0],
                                                        self.args[1])


class BaseChecker:
    """Abstract generic parser for expressions referencing Instance objects."""

    # AST elements

    class Atom (six.with_metaclass(abc.ABCMeta)):

        def __call__(self, *args):
            try:
                return self.evaluate(*args)
            except (KeyError, FilterExprError):
                raise
            except Exception as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = FilterExprError(self, e)
                six.reraise(new_e.__class__, new_e, exc_traceback)

        @abc.abstractmethod
        def evaluate(self, *args):
            pass

        @abc.abstractmethod
        def copy(self):
            pass

        @abc.abstractmethod
        def validate(self, allowed):
            pass

        @abc.abstractmethod
        def __str__(self):
            pass

        @abc.abstractmethod
        def del_ids(self, dels):
            pass

    class AtomConstant (Atom):
        """Constant value."""
        def __init__(self, value):
            self._value = value

        def evaluate(self, *args):
            return self._value

        def copy(self):
            return BaseChecker.AtomConstant(self._value)

        def validate(self, allowed):
            pass

        def __str__(self):
            if isinstance(self._value, six.string_types):
                return "'%s'" % self._value
            else:
                return repr(self._value)

        def del_ids(self, dels):
            return self

    class AtomVar (Atom):
        """Variable reference."""
        def __init__(self, id):
            self._id = id

        def evaluate(self, var_dict):
            return var_dict[self._id]

        def copy(self):
            return BaseChecker.AtomVar(self._id)

        def validate(self, allowed):
            if self._id not in allowed:
                raise FilterUnallowedError(self._id, self)

        def __str__(self):
            return str(self._id)

        def del_ids(self, dels):
            if len(dels) == 0 or self._id in dels:
                del self
                return None
            return self

    class AtomVarExists (Atom):
        """Whether a variable exists."""
        def __init__(self, id):
            self._id = id

        def evaluate(self, var_dict):
            return self._id in var_dict

        def copy(self):
            return BaseChecker.AtomVarExists(self._id)

        def validate(self, allowed):
            if self._id not in allowed:
                raise FilterUnallowedError(self._id, self)

        def __str__(self):
            return "exists(%s)" % self._id

        def del_ids(self, dels):
            if len(dels) == 0 or self._id in dels:
                del self
                return None
            return self

    class AtomList (Atom):
        """List."""
        def __init__(self, items):
            self._items = items

        def evaluate(self, var_dict):
            return [e(var_dict) for e in self._items]

        def copy(self):
            return BaseChecker.AtomList([e.copy() for e in self._items])

        def validate(self, allowed):
            for e in self._items:
                e.validate(allowed)

        def __str__(self):
            return '[%s]' % ', '.join(str(e) for e in self._items)

        def del_ids(self, dels):
            items = [e.del_ids(dels) for e in self._items]
            items = [e for e in items if e is not None]
            if len(items) == 0:
                del self
                return None
            else:
                self._items = items
                return self

    class AtomBool (Atom):
        """Abstract boolean expression."""
        def __init__(self, e1, e2):
            self._e1 = e1
            self._e2 = e2

        def copy(self):
            return self.__class__(self._e1.copy(), self._e2.copy())

        def validate(self, allowed):
            self._e1.validate(allowed)
            self._e2.validate(allowed)

    class AtomCmp (AtomBool):
        """Abstract boolean comparison."""
        def del_ids(self, dels):
            self._e1 = self._e1.del_ids(dels)
            self._e2 = self._e2.del_ids(dels)
            if self._e1 is None or self._e2 is None:
                del self
                return None
            return self

    class AtomNEQ (AtomCmp):
        """Boolean 'not equal'."""
        def evaluate(self, *args):
            return self._e1(*args) != self._e2(*args)

        def __str__(self):
            return "%s != %s" % (self._e1, self._e2)

    class AtomEQ (AtomCmp):
        """Boolean 'equal'."""
        def evaluate(self, *args):
            return self._e1(*args) == self._e2(*args)

        def __str__(self):
            return "%s == %s" % (self._e1, self._e2)

    class AtomLT (AtomCmp):
        """Boolean 'less than'."""
        def evaluate(self, *args):
            return self._e1(*args) < self._e2(*args)

        def __str__(self):
            return "%s < %s" % (self._e1, self._e2)

    class AtomLE (AtomCmp):
        """Boolean 'less or equal'."""
        def evaluate(self, *args):
            return self._e1(*args) <= self._e2(*args)

        def __str__(self):
            return "%s <= %s" % (self._e1, self._e2)

    class AtomGT (AtomCmp):
        """Boolean 'greater than'."""
        def evaluate(self, *args):
            return self._e1(*args) > self._e2(*args)

        def __str__(self):
            return "%s > %s" % (self._e1, self._e2)

    class AtomGE (AtomCmp):
        """Boolean 'greater or equal'."""
        def evaluate(self, *args):
            return self._e1(*args) >= self._e2(*args)

        def __str__(self):
            return "%s >= %s" % (self._e1, self._e2)

    class AtomIN (AtomCmp):
        """Boolean 'in'."""
        def evaluate(self, *args):
            e1 = self._e1(*args)
            e2 = self._e2(*args)
            return e1 in e2

        def __str__(self):
            return "%s in %s" % (self._e1, self._e2)

    class AtomBoolOp (AtomBool):
        """Abstract boolean operation."""
        def del_ids(self, dels):
            self._e1 = self._e1.del_ids(dels)
            self._e2 = self._e2.del_ids(dels)
            if self._e1 is None:
                return self._e2
            elif self._e2 is None:
                return self._e1
            return self

    class AtomOR (AtomBoolOp):
        """Boolean 'or'."""
        def evaluate(self, *args):
            return self._e1(*args) or self._e2(*args)

        def __str__(self):
            res = ""
            if isinstance(self._e1, BaseChecker.AtomOR) or \
               isinstance(self._e1, BaseChecker.AtomCmp):
                res += "%s" % self._e1
            else:
                res += "( %s )" % self._e1
            res += " || "
            if isinstance(self._e2, BaseChecker.AtomOR) or \
               isinstance(self._e2, BaseChecker.AtomCmp):
                res += "%s" % self._e2
            else:
                res += "( %s )" % self._e2
            return res

    class AtomAND (AtomBoolOp):
        """Boolean 'and'."""
        def evaluate(self, *args):
            return self._e1(*args) and self._e2(*args)

        def __str__(self):
            res = ""
            if isinstance(self._e1,
                          (BaseChecker.AtomAND, BaseChecker.AtomCmp,
                           BaseChecker.AtomNOT)):
                res += "%s" % self._e1
            else:
                res += "( %s )" % self._e1
            res += " && "
            if isinstance(self._e2,
                          (BaseChecker.AtomAND, BaseChecker.AtomCmp,
                           BaseChecker.AtomNOT)):
                res += "%s" % self._e2
            else:
                res += "( %s )" % self._e2
            return res

    class AtomNOT (Atom):
        """Boolean 'not'."""
        def __init__(self, e):
            self._e = e

        def copy(self):
            return self.__class__(self._e.copy())

        def validate(self, allowed):
            self._e.validate(allowed)

        def del_ids(self, dels):
            self._e = self._e.del_ids(dels)
            if self._e is None:
                return None
            return self

        def evaluate(self, *args):
            return not self._e(*args)

        def __str__(self):
            if isinstance(self._e, (BaseChecker.AtomAND, BaseChecker.AtomOR)):
                return "! (" + str(self._e) + ")"
            else:
                return "! " + str(self._e)

    class AtomOp (Atom):
        """Abstract arithmetic operation."""
        def __init__(self, e1, e2):
            self._e1 = e1
            self._e2 = e2

        def copy(self):
            return self.__class__(self._e1.copy(), self._e2.copy())

        def validate(self, allowed):
            self._e1.validate(allowed)
            self._e2.validate(allowed)

        def del_ids(self, dels):
            self._e1 = self._e1.del_ids(dels)
            self._e2 = self._e2.del_ids(dels)
            if self._e1 is None or self._e2 is None:
                del self
                return None
            else:
                return self

    class AtomUMINUS (Atom):
        """Arithmetic negation."""
        def __init__(self, e):
            self._e = e

        def evaluate(self, *args):
            return - self._e(*args)

        def copy(self):
            return self.__class__(self._e.copy())

        def __str__(self):
            return "- %s" % self._e

        def validate(self, allowed):
            self._e.validate(allowed)

        def del_ids(self, dels):
            self._e = self._e.del_ids(dels)
            if self._e is None:
                del self
                return None
            else:
                return self

    class AtomPLUS (AtomOp):
        """Arithmetic sum."""
        def evaluate(self, *args):
            return self._e1(*args) + self._e2(*args)

        def __str__(self):
            return "%s + %s" % (self._e1, self._e2)

    class AtomMINUS (AtomOp):
        """Arithmetic substract."""
        def evaluate(self, *args):
            return self._e1(*args) - self._e2(*args)

        def __str__(self):
            return "%s - %s" % (self._e1, self._e2)

    class AtomTIMES (AtomOp):
        """Arithmetic multiply."""
        def evaluate(self, *args):
            return self._e1(*args) * self._e2(*args)

        def __str__(self):
            return "%s * %s" % (self._e1, self._e2)

    class AtomDIVIDE (AtomOp):
        """Arithmetic divide."""
        def evaluate(self, *args):
            return self._e1(*args) / self._e2(*args)

        def __str__(self):
            return "%s / %s" % (self._e1, self._e2)

    class AtomMOD (AtomOp):
        """Arithmetic modulus."""
        def evaluate(self, *args):
            return self._e1(*args) % self._e2(*args)

        def __str__(self):
            return "%s %% %s" % (self._e1, self._e2)

    @staticmethod
    def compile_regex(regex):
        try:
            return re.compile(str(regex))
        except re.error as e:
            _, _, exc_traceback = sys.exc_info()
            new_e = ParseError("Invalid regular expression: %s"
                               "\n  [was] %s: %s" % (regex,
                                                     e.__class__.__name__,
                                                     str(e)))
            six.reraise(new_e.__class__, new_e, exc_traceback)

    class AtomPBIND (AtomOp):
        """Pattern binding (regexp matching)."""
        def __init__(self, *args, **kwargs):
            BaseChecker.AtomOp.__init__(self, *args, **kwargs)
            self._cre2 = BaseChecker.compile_regex(self._e2())

        def evaluate(self, *args):
            e1 = str(self._e1(*args))
            m = self._cre2.match(e1)
            return m is not None

        def __str__(self):
            return "%s =~ %s" % (self._e1, self._e2)

    class AtomNPBIND (AtomOp):
        """Pattern binding (regexp matching)."""
        def __init__(self, *args, **kwargs):
            BaseChecker.AtomOp.__init__(self, *args, **kwargs)
            self._cre2 = BaseChecker.compile_regex(self._e2())

        def evaluate(self, *args):
            e1 = str(self._e1(*args))
            m = self._cre2.match(e1)
            return m is None

        def __str__(self):
            return "%s !~ %s" % (self._e1, self._e2)

    # Tokens
    reserved = {
        'True':   'TRUE',
        'False':  'FALSE',
        'in':     'IN',
        'not':    'NOT_STR',
        'exists': 'EXISTS',
    }

    tokens = [
        'STRING',
        'NUMBER',
        'LPAR', 'RPAR',
        'LSQB', 'RSQB', 'COMMA',
        'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
        'AND', 'OR', 'NOT',
        'PBIND', 'NPBIND',
        'ID',
    ] + list(reserved.values())

    t_STRING = r"'[^']+'"

    def t_NUMBER(self, t):
        r'\d+\.?\d*'
        t.value = utils.str2num(t.value)
        assert not isinstance(t.value, str)
        return t

    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_LSQB = r'\['
    t_RSQB = r'\]'
    t_COMMA = r','
    t_EQ = r'=='
    t_NEQ = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_NOT = r'!'
    t_PBIND = r'=~'
    t_NPBIND = r'!~'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # check for reserved words
        t.type = self.reserved.get(t.value, 'ID')
        if t.type == "TRUE":
            t.value = True
        elif t.type == "FALSE":
            t.value = False
        return t

    # Ignored characters
    t_ignore = " \t"

    def t_error(self, t):
        raise ParseError("Illegal character in expression: %s" % t.value[0])

    # Parsing rules

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'MOD'),
        ('right', 'UMINUS'),
        ('left', 'AND', 'OR'),
        ('right', 'NOT'),
    )

    def p_bool(self, t):
        '''
        bool : TRUE
             | FALSE
        '''
        t[0] = self.AtomConstant(t[1])

    def p_bool_exists(self, t):
        '''
        bool : EXISTS LPAR ID RPAR
        '''
        t[0] = self.AtomVarExists(t[3])

    def p_bool_group(self, t):
        'bool : LPAR bool RPAR'
        t[0] = t[2]

    def p_bool_cmp(self, t):
        '''
        bool : expression cmp_op expression
        '''
        t[0] = t[2](t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_bool_cmp_op(self, t):
        '''
        cmp_op : EQ
               | NEQ
               | LT
               | LE
               | GT
               | GE
               | PBIND
               | NPBIND
        '''
        if t[1] == "==":
            t[0] = self.AtomEQ
        elif t[1] == "!=":
            t[0] = self.AtomNEQ
        elif t[1] == "<":
            t[0] = self.AtomLT
        elif t[1] == "<=":
            t[0] = self.AtomLE
        elif t[1] == ">":
            t[0] = self.AtomGT
        elif t[1] == ">=":
            t[0] = self.AtomGE
        elif t[1] == "=~":
            t[0] = self.AtomPBIND
        elif t[1] == "!~":
            t[0] = self.AtomNPBIND
        else:
            raise Exception

    def p_bool_cmp_multi(self, t):
        '''
        bool : expression cmp_op expression cmp_multi_rest
        '''
        left = t[2](t[1], t[3])
        cls, expression, rest = t[4]
        right = cls(t[3], expression)
        if rest is not None:
            right = self.AtomAND(right, rest)
        t[0] = self.AtomAND(left, right)

    def p_bool_cmp_multi_rest(self, t):
        '''
        cmp_multi_rest : cmp_op expression
                       | cmp_op expression cmp_multi_rest
        '''
        if len(t) == 3:
            t[0] = (t[1], t[2], None)
        elif len(t) == 4:
            cls, expression, rest = t[3]
            right = cls(t[2], expression)
            if rest is not None:
                right = self.AtomAND(right, rest)
            t[0] = (t[1], t[2], right)
        else:
            raise Exception

    def p_bool_in(self, t):
        '''
        bool : expression IN expression
        '''
        t[0] = self.AtomIN(t[1], t[3])

    def p_bool_not_in(self, t):
        '''
        bool : expression NOT_STR IN expression
        '''
        t[0] = self.AtomNOT(self.AtomIN(t[1], t[4]))

    def p_bool_bool(self, t):
        '''
        bool : bool OR  bool
             | bool AND bool
        '''
        if t[2] == "||":
            t[0] = self.AtomOR(t[1], t[3])
            if isinstance(t[1], self.AtomConstant):
                if t[1]():
                    t[0] = t[1]
                else:
                    t[0] = t[3]
        else:
            t[0] = self.AtomAND(t[1], t[3])
            if isinstance(t[1], self.AtomConstant):
                if t[1]():
                    t[0] = t[3]
                else:
                    t[0] = t[1]

    def p_bool_not(self, t):
        'bool : NOT bool %prec NOT'
        t[0] = self.AtomNOT(t[2])

    def p_bool_id(self, t):
        'bool : ID'
        t[0] = self.AtomVar(t[1])

    def p_expression_group(self, t):
        'expression : LPAR expression RPAR'
        t[0] = t[2]

    def p_expression_list(self, t):
        'expression : LSQB list RSQB'
        t[0] = self.AtomList(t[2])

    def p_expression_list_empty(self, t):
        'expression : LSQB RSQB'
        t[0] = self.AtomList([])

    def p_expression_list_full(self, t):
        '''
        list : expression
             | expression COMMA list
        '''
        if len(t) == 2:
            t[0] = [t[1]]
        elif len(t) == 4:
            t[0] = [t[1]] + t[3]
        else:
            raise Exception

    def p_expression_uminus(self, t):
        'expression : MINUS expression %prec UMINUS'
        t[0] = self.AtomUMINUS(t[2])
        if isinstance(t[2], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_plus(self, t):
        'expression : expression PLUS expression'
        t[0] = self.AtomPLUS(t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_minus(self, t):
        'expression : expression MINUS expression'
        t[0] = self.AtomMINUS(t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_times(self, t):
        'expression : expression TIMES expression'
        t[0] = self.AtomTIMES(t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_divide(self, t):
        'expression : expression DIVIDE expression'
        t[0] = self.AtomDIVIDE(t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_mod(self, t):
        'expression : expression MOD expression'
        t[0] = self.AtomMOD(t[1], t[3])
        if isinstance(t[1], self.AtomConstant) and \
           isinstance(t[3], self.AtomConstant):
            t[0] = self.AtomConstant(t[0]())

    def p_expression_number(self, t):
        '''
        expression : NUMBER
                   | TRUE
                   | FALSE
        '''
        t[0] = self.AtomConstant(t[1])

    def p_expression_str(self, t):
        'expression : STRING'
        t[0] = self.AtomConstant(t[1][1:-1])

    def p_expression_id(self, t):
        'expression : ID'
        t[0] = self.AtomVar(t[1])

    def p_error(self, t):
        if t:
            raise ParseError("Syntax error at '%s'" % t)
        else:
            raise ParseError("Unexpected end of filter expression")

    # Common interface

    # Each subclass must:
    # - define a '_checker' global attribute to hold the parser
    # - define a '_start' global attribute to hold the name of the starting
    #   rule
    # - the rule identified by '_start' must store the resulting AST into
    #   'self._result'

    @classmethod
    def _get(cls):
        """Get the parser."""
        if cls._checker is None:
            cls._checker = cls()
            cls._checker._build()
        return cls._checker

    def _build(self):
        """Build a new parser."""
        self._lexer = lex.lex(object=self, debug=0)
        self._parser = yacc.yacc(module=self, debug=0, write_tables=0,
                                 start=self._start)

    @classmethod
    def parse(cls, expression):
        """Parse 'expression'."""
        p = cls._get()
        try:
            p._parser.parse(expression, lexer=p._lexer, debug=0)
        except Exception as e:
            _, _, exc_traceback = sys.exc_info()
            new_e = ParseError("While parsing: %r"
                               "\n  [was] %s: %s" % (expression,
                                                     e.__class__.__name__,
                                                     str(e)))
            six.reraise(new_e.__class__, new_e, exc_traceback)
        return p._result


class _FilterChecker (BaseChecker):
    """Parser for Instance filters."""

    # AST elements

    class AtomFilter:
        def __init__(self, filter_):
            self._filter = filter_
            self._constant = self._is_constant()

        def __call__(self, instance):
            try:
                return self._filter(instance)
            except FilterExprError as e:
                _, _, exc_traceback = sys.exc_info()
                new_e = FilterEvalError(self, instance, e)
                six.reraise(new_e.__class__, new_e, exc_traceback)

        def copy(self):
            return _FilterChecker.AtomFilter(self._filter.copy())

        def __str__(self):
            return str(self._filter)

        def validate(self, allowed):
            self._filter.validate(allowed)

        def add(self, other):
            """Add a copy of 'other' into self."""
            self._filter = BaseChecker.AtomAND(self._filter,
                                               other._filter.copy())
            self._constant = self._is_constant()
            return self

        def _is_constant(self):
            return isinstance(self._filter, BaseChecker.AtomConstant)

        @property
        def constant(self):
            return self._constant

    # Parsing rules

    def p_filter(self, t):
        'filter : bool'
        self._result = _FilterChecker.AtomFilter(t[1])

    # Interface
    _checker = None
    _start = "filter"


def _filter_optimize(opt_dict, expression):
    """Try to optimize a filter into a `dict`."""
    if isinstance(expression, _FilterChecker.AtomFilter):
        return _filter_optimize(opt_dict, expression._filter)

    elif isinstance(expression, BaseChecker.AtomAND):
        return (_filter_optimize(opt_dict, expression._e1) and
                _filter_optimize(opt_dict, expression._e2))

    elif isinstance(expression, BaseChecker.AtomEQ):
        if (isinstance(expression._e1, BaseChecker.AtomVar) and
            isinstance(expression._e2, BaseChecker.AtomConstant)):
            if expression._e1._id in opt_dict:
                return opt_dict[expression._e1._id] == expression._e2._value
            opt_dict[expression._e1._id] = expression._e2._value
            return True
        elif (isinstance(expression._e1, BaseChecker.AtomConstant) and
              isinstance(expression._e2, BaseChecker.AtomVar)):
            if expression._e2._id in opt_dict:
                return opt_dict[expression._e2._id] == expression._e1._value
            opt_dict[expression._e2._id] = expression._e1._value
            return True
        else:
            return False

    else:
        return False


class Filter:
    """Boolean expression to check against a dict-like object.

    Any dict-like object can be checked against a filter to see if it
    positively matches the constraints in the filter, where variable references
    in the filter are used as keys to the target dict-like object.

    Filters are widely used to select specific contents of an instance group by
    selecting only those instances that match the filter.


    Parameters
    ----------
    filters : optional
        Filters to `AND` together.


    Raises
    ------
    ParseError
        Filter cannot be parsed (invalid syntax).


    Notes
    -----
    Elements in `filters` are `AND`'ed together into a single filter
    expression. Each element can take one of the following forms:

    * `str`: A textual filter that will be parsed.

    * `dict`: Shorthand where every ``key=value`` pair is considered a variable
      and value equality test.

    * `Filter`
    * `PFilter`

    Filters are transparently optimized for `AND`'ed expressions that check if
    a variable is equal to a given value.

    The available syntactical tokens are:

     ============================  ==========================
     Group expressions             ``( ... )``
     Lists of expressions          ``[ ... ]``
     Check membership              ``... in ...``, ``... not in ...``
     Reference other variables     VAR
     Check if a variable exists    ``exists(`` VAR ``)``
     Boolean values                ``True`` or ``False``
     Explicit numbers and strings  ``number`` or ``'string'``
     Simple math operators         ``+``, ``-``, ``*``, ``/``
     Comparisons                   ``<``, ``<=``, ``>``, ``>=``, ``==``, ``!=``
     Pattern binding               ``=~``, ``!~``
     Boolean operations            ``||``, ``&&``, ``!``
     ============================  ==========================

    In order to streamline the syntax of range checks, "multi-comparisons" are
    also available.

    Pattern binding operators match the left-hand argument with the right-hand
    regular expression. Both sides are converted into a string regardless of
    their type, and the the regular expression must match the beginning of the
    left-hand string.


    See also
    --------
    match


    Examples
    --------
    Filters are initially created by parsing strings, and can be composed using
    the sumation operator:

    >>> f = Filter("a < 3")
    >>> f & Filter("b == 4")
    Filter("a < 3 && b == 4")
    >>> f &= Filter("b == 4")
    >>> f
    Filter("a < 3 && b == 4")

    "Multi-comparisons" can be used as a shorthand for range checks:

    >>> Filter("1 < a < 3")
    Filter("1 < a && a < 3")
    >>> Filter("1 < a < b < 3")
    Filter("1 < a && a < b && b < 3")

    Once a filter has been "compiled", it can be later matched against
    :class:`dict`-like objects:

    >>> f.match(dict(a = 2, b = 4))
    True
    >>> f.match(dict(a = 3, b = 4))
    False

    Using dictionaries instead of strings makes ``f1`` and ``f2`` equivalent:

    >>> d = {"VAR1": 1, "VAR2": 2}
    >>> f1 = Filter(d)
    >>> f2 = Filter("VAR1 == 1 && VAR2 == 2")
    >>> str(f1) == str(f2)
    True
    >>> f1.as_dict() == d
    True

    Membership checks can simplify some filters:

    >>> Filter("VAR1 in [1, 3, 5]").match(dict(VAR1=3))
    True
    >>> Filter("VAR1 not in [1, 3, 5]").match(dict(VAR1=10))
    True

    """
    def __init__(self, *filters):
        self._expression = self._parse("True")
        self._dict = None

        if len(filters) == 0:
            return

        for f in filters:
            if isinstance(f, six.string_types):
                ff = self._parse(f)
                f = Filter()
                f._expression = ff
            elif isinstance(f, dict):
                ff = Filter()
                ff._dict = f
                f = ff
            elif isinstance(f, PFilter):
                f = f.realize()
            self._merge(f)

        self._optimize()

    @staticmethod
    def _parse(expression):
        return _FilterChecker.parse(expression)

    def _optimize(self):
        if self._expression.constant:
            return
        opt_dict = {}
        if _filter_optimize(opt_dict, self._expression):
            self._expression = self._parse("True")
            self._dict = opt_dict
        else:
            self._dict = None
        # sanity checks
        if self._dict is not None:
            assert self._expression.constant and self._expression({})

    def _merge(self, other):
        """Merge a Filter instance into this one."""
        if not isinstance(other, Filter):
            raise TypeError("invalid Filter type, found '%s'" % repr(other))

        if self._dict is None:
            self_expr = self._expression
        else:
            self_expr = self._parse(str(self))

        self_expr.add(self._parse(str(other)))
        self._expression = self._parse(str(self_expr))
        self._optimize()

    def __str__(self):
        """Return a string representation of the filter."""
        if self._dict is None:
            return str(self._expression)
        elif self._dict is not None:
            res = []
            for key, val in sorted(self._dict.items()):
                res.append("%s == %r" % (key, val))
            return " && ".join(res)

    def __repr__(self):
        return "Filter(\"%s\")" % str(self)

    def validate(self, allowed):
        """Validate that variables in the filter are present in the given set.

        Parameters
        ----------
        allowed : set of variable names
            Set of variable names to allow on the filter.


        Raises
        ------
        FilterUnallowedError
            Filter contains an unallowed variable.

        """
        if self._dict is not None:
            for var in self._dict.keys():
                if var not in allowed:
                    raise FilterUnallowedError(var, self)
        else:
            try:
                self._expression.validate(allowed)
            except FilterUnallowedError as e:
                raise FilterUnallowedError(e.args[0], self)

    def as_dict(self):
        """Return a :class:`dict` representation of this filter.

        Returns
        -------
        dict or None : The optimized dict representation of this filter.

        Notes
        -----
        If there is no optimized dict representation available, returns
        ``None``.

        """
        if self._dict is not None:
            return dict(self._dict)
        else:
            return None

    def match(self, source):
        """Check if the given :class:`dict` matches this filter.

        Parameters
        ----------
        source : dict-like
            Dictionary to match this filter against.

        Returns
        -------
        bool : Whether the match is positive or not.

        Raises
        ------
        FilterError
            Filter contains a variable name not present in `source`.
        FilterEvalError
            An error happened while evaluating the filter.

        See also
        --------
        validate

        """
        if self._dict is None and self._expression.constant:
            return self._expression({})
        assert isinstance(source, dict)

        try:
            if self._expression is not None:
                if not self._expression(source):
                    return False

            if self._dict is not None:
                for key, val in six.iteritems(self._dict):
                    if source[key] != val:
                        return False

        except KeyError as e:
            raise FilterError(e.args[0], self)

        return True

    @utils.deprecated
    def __iadd__(self, other):
        """Add an `AND`'ed filter object."""
        return self.__iand__(other)

    @utils.deprecated
    def __add__(self, other):
        """Add two `AND`'ed filters together into a new one."""
        return self.__and__(other)

    def __iand__(self, other):
        if not isinstance(other, Filter):
            other = Filter(other)
        self._merge(other)
        return self

    def __and__(self, other):
        res = Filter(self)
        res &= other
        return res

    def __or__(self, other):
        return Filter("(%s) || (%s)" % (self, other))


class PFilter (object):
    """Programmatic version of `Filter`.

    Provides a programmatic interface to constructing filters.

    Notes
    -----
    Unless noted, it supports the same operators as regular `Filter` instances.

    Boolean operations ``||``, ``&&`` and ``!`` must be written as ``|``, ``&``
    and ``~`` (respectively); just be sure to use parentheses around the groups
    you are and'ing or or'ing together . Pattern binding is not supported.


    Examples
    --------
    Filters constructed from strings or programmatically are equivalent (just
    remember to use parentheses):

    >>> Filter("!a || b % 2 == 0")
    Filter("( ! a ) || b % 2 == 0")
    >>> v_ = PFilter()
    >>> (~ v_.a) | (v_.b % 2 == 0)
    Filter("( ! a ) || b % 2 == 0")

    Programmatic filters can also be combined with other filters:

    >>> (v_.c == "foo") | Filter("b == 2")
    Filter("c == 'foo' || b == 2")

    An actual `Filter` instance can be obtained with the `realize` method:

    >>> isinstance(v_.a == 1, Filter)
    False
    >>> isinstance((v_.a == 1).realize(), Filter)
    True

    """
    def __init__(self, left=None):
        if left is None:
            left = ""
        else:
            left = str(left)
        self._other = left

    def __str__(self):
        return str(self.realize())

    def __repr__(self):
        return repr(self.realize())

    def realize(self):
        return Filter(self._other)

    def _construct(self, other):
        res = PFilter()
        res._other = other
        return res

    def __getattr__(self, name):
        if self._other == "":
            return self._construct(name)
        else:
            return self._construct("%s %s" % (self._other, name))

    # Generic operation handler

    def _operate(self, op, other, as_filter=False):
        if isinstance(other, PFilter):
            res_fmt = "(%s %s %s)"
            return self._construct(res_fmt % (self._other, op, other._other))
        elif isinstance(other, six.string_types) and not as_filter:
            res_fmt = "(%s %s '%s')"
            return self._construct(res_fmt % (self._other, op, other))
        else:
            res_fmt = "(%s %s %s)"
            return self._construct(res_fmt % (self._other, op, other))

    # Arithmetic

    def __neg__(self, other):
        return self._operate("-", other)

    def __add__(self, other):
        return self._operate("+", other)

    def __sub__(self, other):
        return self._operate("-", other)

    def __mul__(self, other):
        return self._operate("*", other)

    def __div__(self, other):
        return self._operate("/", other)

    def __mod__(self, other):
        return self._operate("%", other)

    # Comparison

    def __lt__(self, other):
        return self._operate("<", other)

    def __le__(self, other):
        return self._operate("<=", other)

    def __gt__(self, other):
        return self._operate(">", other)

    def __ge__(self, other):
        return self._operate(">=", other)

    def __eq__(self, other):
        return self._operate("==", other)

    def __ne__(self, other):
        return self._operate("!=", other)

    # Boolean

    def __and__(self, other):
        return self._operate("&&", other, as_filter=True)

    def __or__(self, other):
        return self._operate("||", other, as_filter=True)

    def __invert__(self):
        return self._construct("!(%s)" % self._other)


__all__ = [
    "ParseError",
    "FilterError", "FilterExprError", "FilterEvalError", "FilterUnallowedError",
    "BaseChecker", "Filter", "PFilter",
]
