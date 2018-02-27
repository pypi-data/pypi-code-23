
from pyparsing import Combine, Optional, Word, Keyword, Literal, QuotedString, ZeroOrMore, oneOf, opAssoc, alphas, \
    alphanums, nums, infixNotation, ParserElement

from ...logger import logger

from lib.lib_interfaces import RookInvalidArithmeticPath
from .basic_path import BasicPath
from ..namespaces.python_object_namespace import PythonObjectNamespace


# Some future ideas for this class:
# 1. Make this class self-contained without relying on BasicPath.
# 2. Add support for functions, lists and more...
# 3. Make this class the default class in some/all use cases.


class ArithmeticPath(object):

    NAME = 'calc'

    def __init__(self, configuration, factory):
        logger.info("Building Arithmetic Path")

        string_path = configuration['path']
        syntax = self._build_syntax()

        parsed = syntax.parseString(string_path, parseAll=True)
        if len(parsed) != 1:
            raise RookInvalidArithmeticPath(configuration)
        self._expr = parsed[0]

    def read_from(self, root_namespace):
        result = self._expr.eval(root_namespace)
        return PythonObjectNamespace(result)

    def write_to(self, root_namespace, value):
        raise NotImplementedError()

    @staticmethod
    def _build_syntax():

        class Operator(object):
            def eval(self, namespace):
                raise NotImplementedError()

            @staticmethod
            def _operatorOperands(token_list):
                """generator to extract operators and operands in pairs"""
                it = iter(token_list)
                while 1:
                    try:
                        yield (next(it), next(it))
                    except StopIteration:
                        break

        class EvalValue(Operator):
            def __init__(self, value):
                self._value = value

            def eval(self, namespace):
                return self._value

        class EvalPath(Operator):
            def __init__(self, tokens):
                self._path = BasicPath(tokens[0])

            try:
                PRIMITIVE_VALUES = (str, unicode, int, long, float, list)
            except NameError:
                PRIMITIVE_VALUES = (str, int, float, list)

            def eval(self, namespace):
                value = self._path.read_from(namespace).obj
                if isinstance(value, self.PRIMITIVE_VALUES):
                    return value
                else:
                    # TODO - this needs to be changed if we want to have arithmetic path as the default path
                    raise ValueError("Value is not supported by ArithmeticPath!", value)

        class EvalList(Operator):
            """Class to evaluate expressions building a list"""

            def __init__(self, tokens):
                self.tokens = tokens[1:-1:2]

            def eval(self, namespace):
                return [token.eval(namespace) for token in self.tokens]

        class EvalSignOp(Operator):
            """Class to evaluate expressions with a leading + or - sign"""

            def __init__(self, tokens):
                self.sign, self.value = tokens[0]

            def eval(self, namespace):
                mult = {'+': 1, '-': -1}[self.sign]
                return mult * self.value.eval(namespace)

        class EvalMultOp(Operator):
            """Class to evaluate multiplication and division expressions"""

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, namespace):
                result = self.value[0].eval(namespace)
                for op, val in self._operatorOperands(self.value[1:]):
                    if op == '*':
                        result *= val.eval(namespace)
                    elif op == '/':
                        result /= val.eval(namespace)
                return result

        class EvalAddOp(Operator):
            """Class to evaluate addition and subtraction expressions"""

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, namespace):
                result = self.value[0].eval(namespace)
                for op, val in self._operatorOperands(self.value[1:]):
                    if op == '+':
                        result += val.eval(namespace)
                    elif op == '-':
                        result -= val.eval(namespace)
                return result

        class AndOrOp(Operator):

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, namespace):
                result = bool(self.value[0].eval(namespace))
                for op, val in self._operatorOperands(self.value[1:]):
                    if op == 'and':
                        result = result and val.eval(namespace)
                    elif op == 'or':
                        result = result or val.eval(namespace)
                return result

        class EvalComparisonOp(Operator):
            "Class to evaluate comparison expressions"
            _opMap = {
                "<": lambda a, b: a < b,
                "<=": lambda a, b: a <= b,
                ">": lambda a, b: a > b,
                ">=": lambda a, b: a >= b,
                "!=": lambda a, b: a != b,
                "=": lambda a, b: a == b,
                "LT": lambda a, b: a < b,
                "LE": lambda a, b: a <= b,
                "GT": lambda a, b: a > b,
                "GE": lambda a, b: a >= b,
                "NE": lambda a, b: a != b,
                "EQ": lambda a, b: a == b,
                "<>": lambda a, b: a != b,
                "in": lambda a, b: a in b,
            }

            def __init__(self, tokens):
                self.value = tokens[0]

            def eval(self, namespace):
                val1 = self.value[0].eval(namespace)
                for op, val in self._operatorOperands(self.value[1:]):
                    fn = self._opMap[op]
                    val2 = val.eval(namespace)
                    if not fn(val1, val2):
                        break
                    val1 = val2
                else:
                    return True
                return False

        boolean = Keyword('True').setParseAction(lambda tokens: EvalValue(True)) | \
            Keyword('False').setParseAction(lambda tokens: EvalValue(False))
        integer = Combine(Optional(oneOf("+ -")) + Word(nums)).setName("integer") \
            .setParseAction(lambda tokens: EvalValue(int(tokens[0])))
        real = Combine(Optional(oneOf("+ -")) + Word(nums) + "." + Optional(Word(nums)) +
                       Optional(oneOf("e E") + Optional(oneOf("+ -")) + Word(nums))) \
            .setName("real").setParseAction(lambda tokens: EvalValue(float(tokens[0])))
        string = QuotedString('"').setName("string").setParseAction(lambda tokens: EvalValue(str(tokens[0])))

        values = boolean | string | real | integer

        namespace_path = Word(alphas, alphanums + ".[]'\"").setName("path").setParseAction(EvalPath)

        single_value = values | namespace_path
        list_value = (Literal("[") + ZeroOrMore(single_value + Literal(",")) + Optional(single_value) + Literal("]")). \
            setName("list").setParseAction(lambda tokens: EvalList(tokens))
        atom = single_value | list_value

        sign_op = oneOf('+ -')
        mult_op = oneOf('* /')
        plus_op = oneOf('+ -')
        and_op = Literal('and')
        or_op = Literal('or')
        comparison_op = oneOf("< <= > >= != = <>") ^ Keyword("LT") ^ Keyword("GT") ^ Keyword("LE") ^ \
                Keyword("GE") ^ Keyword("EQ") ^ Keyword("NE") ^ Keyword("in")

        expr = infixNotation(atom,
                             [
                                (sign_op, 1, opAssoc.RIGHT, EvalSignOp),
                                (mult_op, 2, opAssoc.LEFT, EvalMultOp),
                                (plus_op, 2, opAssoc.LEFT, EvalAddOp),
                                (comparison_op, 2, opAssoc.LEFT, EvalComparisonOp),
                                (and_op, 2, opAssoc.LEFT, AndOrOp),
                                (or_op, 2, opAssoc.LEFT, AndOrOp),
                            ])

        return expr
