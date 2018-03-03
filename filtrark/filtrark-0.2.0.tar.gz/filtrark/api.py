from typing import List, Union, Callable
from .string_parser import StringParser
from .expression_parser import ExpressionParser
from .type_definitions import TermTuple


def string(domain: List[Union[str, TermTuple]]) -> str:
    parser = StringParser()
    return parser.parse(domain)


def expression(domain: List[Union[str, TermTuple]]) -> Callable:
    parser = ExpressionParser()
    return parser.parse(domain)
