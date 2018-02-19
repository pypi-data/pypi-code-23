from typing import NewType, List, Tuple, Union

TermTuple = NewType('TermTuple', Tuple[str, str, Union[str, float]])


class Filtrark:
    def __init__(self) -> None:
        self.term_operators = {
            '=': '=', '!=': '<>', '<=': '<=', '<': '<',
            '>': '>', '>=': '>=', 'in': 'in'}

        self.binary_operators = {
            '&': lambda a, b: a + ' AND ' + b,
            '|': lambda a, b: a + ' OR ' + b}

        self.unary_operators = {
            '!': lambda a: 'NOT ' + a}

    def parse(self, domain: List[Union[str, TermTuple]]) -> str:
        stack = []
        for item in list(reversed(domain)):
            if item in self.binary_operators:
                first_operand = stack.pop()
                second_operand = stack.pop()
                stack.append(self.binary_operators[item](
                    first_operand, second_operand))
            elif item in self.unary_operators:
                operand = stack.pop()
                stack.append(self.unary_operators[item](operand))

            stack = self._default_join(stack)

            if isinstance(item, tuple):
                result = self._parse_term(item)
                stack.append(result)

        result = self._default_join(stack)[0]
        return result

    def _default_join(self, stack: List[Union[str, TermTuple]]
                      ) -> List[Union[str, TermTuple]]:
        if len(stack) == 2:
            first_operand = stack.pop()
            second_operand = stack.pop()
            stack.append(self.binary_operators['&'](
                first_operand, second_operand))
        return stack

    def _match_term_operator(self, operator: str) -> str:
        return self.term_operators.get(operator)

    def _parse_term(self, term_tuple: TermTuple) -> str:
        field, operator, value = term_tuple
        operator = self._match_term_operator(operator)
        result = "{} {} {}".format(field, operator, value)
        return result
