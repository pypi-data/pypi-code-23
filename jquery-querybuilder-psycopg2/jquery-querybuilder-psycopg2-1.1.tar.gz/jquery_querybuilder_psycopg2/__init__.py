import psycopg2.sql as sql


class BaseRuleSetParser(sql.Composable):
    def __init__(self, rule_set):
        super().__init__(rule_set)

        self._composable = self._parse(rule_set)

    def as_string(self, context):
        return self._composable.as_string(context)

    def _parse(self, rule_set):
        if not isinstance(rule_set, dict):
            raise ParseError("Rule Set must be a dictionary")

        if 'condition' in rule_set and 'rules' in rule_set:
            return self._parse_group(rule_set)

        return self._parse_rule(rule_set)

    def _parse_group(self, group):
        condition = group.get('condition')
        if condition not in ('AND', 'OR'):
            raise ParseError(
                "Group requires a 'condition' key with a value of 'AND' or 'OR'")
        condition = sql.SQL(" {} ".format(condition))

        rules = group.get('rules')
        if not isinstance(rules, list):
            raise ParseError(
                "Group requires a 'rules' key with a list value")
        rules = [self._parse(rule_set) for rule_set in rules]

        invert = group.get('not', False)
        if not isinstance(invert, bool):
            raise ParseError(
                "Group 'not' key, if specified, requires a boolean value")

        composable = sql.SQL("({})").format(condition.join(rules))

        if invert:
            composable = sql.SQL("NOT {}").format(composable)

        return composable

    def _parse_rule(self, rule):
        field = rule.get('field')
        if not isinstance(field, str):
            raise ParseError(
                "Rule requires a 'field' key with a string value")
        field = sql.Identifier(field)

        operator = rule.get('operator')
        if not isinstance(operator, str):
            raise ParseError(
                "Rule requires an 'operator' key with a string value")

        value = rule.get('value')

        _operator = operator
        invert = False
        if operator.startswith("not_"):
            _operator = operator[4:]
            invert = True

        sql_generator_name = "{}_operator".format(_operator)
        sql_generator = getattr(self, sql_generator_name, None)

        if isinstance(sql_generator, str):
            # SQL template string
            composable = sql.SQL(sql_generator).format(
                field=field, value=sql.Literal(value))
        elif callable(sql_generator):
            # Function that returns a Composable
            composable = sql_generator(field=field, value=value)
        else:
            raise ParseError("Unknown operator: {}".format(operator))

        if invert:
            composable = sql.SQL("NOT {}").format(composable)

        return composable


# Standard jQuery QueryBuilder operators
class DefaultOperatorMixIn:
    equal_operator = "{field} = {value}"
    in_operator = "{field} = ANY ({value})"

    less_operator = "{field} < {value}"
    less_or_equal_operator = "{field} <= {value}"
    greater_operator = "{field} > {value}"
    greater_or_equal_operator = "{field} >= {value}"

    @staticmethod
    def between_operator(field, value):
        if not isinstance(value, list) or not len(value) == 2:
            raise ParseError(
                "Value for 'between' operator must be a list of two items")

        return sql.SQL("{field} BETWEEN {low_value} AND {high_value}").format(
            field=field, low_value=sql.Literal(value[0]), high_value=sql.Literal(value[1]))

    @staticmethod
    def begins_with_operator(field, value):
        if not isinstance(value, str):
            raise ParseError(
                "Value for 'begins_with' operator must be a string")

        return sql.SQL("{field} LIKE {value}").format(
            field=field, value=sql.Literal("{}%".format(value)))

    @staticmethod
    def contains_operator(field, value):
        if not isinstance(value, str):
            raise ParseError(
                "Value for 'contains' operator must be a string")

        return sql.SQL("{field} LIKE {value}").format(
            field=field, value=sql.Literal("%{}%".format(value)))

    @staticmethod
    def ends_with_operator(field, value):
        if not isinstance(value, str):
            raise ParseError(
                "Value for 'ends_with' operator must be a string")

        return sql.SQL("{field} LIKE {value}").format(
            field=field, value=sql.Literal("%{}".format(value)))

    is_empty_operator = "{field} = ''"
    is_not_empty_operator = "{field} != ''"

    is_null_operator = "{field} IS NULL"
    is_not_null_operator = "{field} IS NOT NULL"


class ParseError(Exception):
    pass


class DefaultRuleSetParser(BaseRuleSetParser, DefaultOperatorMixIn):
    pass
