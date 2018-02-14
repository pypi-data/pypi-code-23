"""Defines the building blocks for SQL expressions.

These classes are meant to be extended for concrete expression
classes and provide most necessary functionality.

Also includes implementation of several SQL operators which
are used in python operators on expression classes.
"""
from .query_components import Referenceable, Selectable

class _ValueExpr(Referenceable, Selectable):
    """An expression that can be used by a BreezeBlocks `Query`.
    
    Using this as a base class for query-bound expressions
    will allow them to use python operators to generate
    BreezeBlocks SQL operators.
    
    Several Built-in methods on this class do not return the
    Python-intuitive value, but an operation from operators
    that can be used in query-building.
    """
    
    def __init__(self):
        raise NotImplementedError()
    
    def _get_ref_field(self, db):
        raise NotImplementedError()
    
    def _get_select_field(self, db):
        raise NotImplementedError()
    
    def _get_params(self):
        """Returns a tuple of the parameters of this expression.
        
        For most expressions this will be an empty tuple, so this
        does not need to be overridden.
        """
        return tuple()
    
    def _get_tables(self):
        raise NotImplementedError()
    
    def as_(self, alias):
        """Returns an aliased version of this expression."""
        return _AliasedExpr(self, alias)
    
    # Comparisons
    def __eq__(self, other):
        return Equal_(self, other)
    
    def __ne__(self, other):
        return NotEqual_(self, other)
    
    def __lt__(self, other):
        return LessThan_(self, other)
    
    def __gt__(self, other):
        return GreaterThan_(self, other)
    
    def __le__(self, other):
        return LessThanEqual_(self, other)
    
    def __ge__(self, other):
        return GreaterThanEqual_(self, other)
    
    # Binary Arithmetic operators
    def __add__(self, other):
        return Plus_(self, other)
    
    def __sub__(self, other):
        return Minus_(self, other)
    
    def __mul__(self, other):
        return Mult_(self, other)
    
    def __truediv__(self, other):
        return Div_(self, other)
    
    def __mod__(self, other):
        return Mod_(self, other)
    
    def __pow__(self, other):
        return Exp_(self, other)
    
    # Unary Arithmetic operators
    def __pos__(self):
        return UnaryPlus_(self)
    
    def __neg__(self):
        return UnaryMinus_(self)

class _AliasedExpr(Selectable):
    """An expression using an alias to change its visible name.
    
    The underlying expression can be anything deriving from
    :class:`_ValueExpr` and providing a :meth:`_ref_field` method that
    returns a string.
    """
    
    def __init__(self, expr, alias):
        if isinstance(expr, _AliasedExpr):
            self.__init__(expr._expr, alias)
        else:
            self._expr = expr
            self._alias = alias
    
    def _get_name(self):
        return self._alias
    
    def _get_select_field(self, db):
        return "{} AS {!s}".format(
            self._expr._get_select_field(db), self._alias)
    
    def _get_params(self):
        return self._expr._get_params()
    
    def _get_tables(self):
        return self._expr._get_tables()

class Value(_ValueExpr):
    """A constant value or literal for safe use in a query."""
    
    def __init__(self, value):
        """Sets value equal to the provided value."""
        self._value = value
    
    def _get_name(self):
        """Constant expressions do not have names."""
        return None
    
    def _get_ref_field(self, db):
        """Returns the parameter placeholder for the specified db."""
        return db._param_marker
    
    def _get_select_field(self, db):
        """Returns the parameter placeholder for the specified db."""
        return self._get_ref_field(db)
    
    def _get_params(self):
        return (self._value,)
    
    def _get_tables(self):
        return set()

class ConstantExpr(Value):
    pass

def _fix_expression(expr):
    if isinstance(expr, _ValueExpr):
        return expr
    else:
        return Value(expr)

# Abstract Operators start here.

class _Operator(_ValueExpr):
    """SQL operator base class."""
    
    def __init__(self):
        raise NotImplementedError()
    
    def _get_name(self):
        """Operators do not have names."""
        return None
    
    def _get_ref_field(self, db):
        raise NotImplementedError()
    
    def _get_select_field(self, db):
        """Selecting operators without aliases uses the reference field."""
        return self._get_ref_field(db)
    
    def _get_params(self):
        raise NotImplementedError()
    
    def _get_tables(self):
        raise NotImplementedError()

class _UnaryOperator(_Operator):
    """SQL Unary Operator"""
    
    def __init__(self, operand):
        self._operand = _fix_expression(operand)
    
    def _get_params(self):
        return self._operand._get_params()
    
    def _get_tables(self):
        return self._operand._get_tables()

class _BinaryOperator(_Operator):
    """SQL Binary Operator"""
    
    def __init__(self, lhs, rhs):
        self._lhs = _fix_expression(lhs)
        self._rhs = _fix_expression(rhs)
    
    def _get_params(self):
        result = []
        result.extend(self._lhs._get_params())
        result.extend(self._rhs._get_params())
        return tuple(result)
    
    def _get_tables(self):
        result = set()
        result.update(self._lhs._get_tables(), self._rhs._get_tables())
        return result

class _ChainableOperator(_Operator):
    """SQL chainable operator.
    
    This can be used to implement operators that are both
    associative and commutative.
    See `Or_`, `And_`, or `Plus_` as an example.
    """
    
    def __init__(self, *operands):
        self._operands = [_fix_expression(expr) for expr in operands]
    
    def _get_params(self):
        result = []
        for operand in self._operands:
            result.extend(operand._get_params())
        return result
    
    def _get_tables(self):
        result = set()
        result.update(*[o._get_tables() for o in self._operands])

# Concrete operators start here.
class Equal_(_BinaryOperator):
    """SQL `=` operator."""
    
    def _get_ref_field(self, db):
        return "({}) = ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class NotEqual_(_BinaryOperator):
    """SQL `!=` or `<>` operator."""
    
    def _get_ref_field(self, db):
        return "({}) <> ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class LessThan_(_BinaryOperator):
    """SQL `<` operator."""
    
    def _get_ref_field(self, db):
        return "({}) < ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class GreaterThan_(_BinaryOperator):
    """SQL `>` operator."""
    
    def _get_ref_field(self, db):
        return "({}) > ({})".format(
                self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class LessThanEqual_(_BinaryOperator):
    """SQL `<=` operator."""
    
    def _get_ref_field(self, db):
        return "({}) <= ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class GreaterThanEqual_(_BinaryOperator):
    """SQL `>=` operator."""
    
    def _get_ref_field(self, db):
        return "({}) >= ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class Plus_(_ChainableOperator):
    """SQL `+` operator."""
    
    def _get_ref_field(self, db):
        return " + ".join(
            ["({})".format(expr._get_ref_field(db)) for expr in self._operands])

class Minus_(_BinaryOperator):
    """SQL `-` operator."""
    
    def _get_ref_field(self, db):
        return "({}) - ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class Mult_(_ChainableOperator):
    """SQL `*` operator."""
    
    def _get_ref_field(self, db):
        return " * ".join(
            ["({})".format(expr._get_ref_field(db)) for expr in self._operands])

class Div_(_BinaryOperator):
    """SQL `/` operator."""
    
    def _get_ref_field(self, db):
        return "({}) / ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class Mod_(_BinaryOperator):
    """SQL `%` operator."""
    
    def _get_ref_field(self, db):
        return "({}) % ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class Exp_(_BinaryOperator):
    """SQL `^` operator."""
    
    def _get_ref_field(self, db):
        return "({}) ^ ({})".format(
            self._lhs._get_ref_field(db), self._rhs._get_ref_field(db))

class UnaryPlus_(_UnaryOperator):
    """SQL Unary `+` operator"""
    
    def _get_ref_field(self, db):
        return "+({})".format(self._operand._get_ref_field(db))

class UnaryMinus_(_UnaryOperator):
    """SQL Unary `-` operator"""
    
    def _get_ref_field(self, db):
        return "-({})".format(self._operand._get_ref_field(db))
