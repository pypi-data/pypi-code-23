# -*- coding: utf-8 -*-


class Criterion(object):
    """
    Criterion class for applying a criteria to our queries.
    A criteria consists of three elements:

    - the queried attributes, an EntityField element if the criteria has a simple operator, another Criteria otherwise
    - an operator, simple or complex, for querying data
    - a value or a list of value to perform the comparision if the criteria has a simple operator, another Criteria
      otherwise

    This criteria is consumed by a QueryBuilder object for returning a new Query object containing a dictionary
    representing the query in Contacthub
    """

    class COMPLEX_OPERATORS:
        """
        List of complex operators handled in Contacthub
        """
        AND = 'and'
        OR = 'or'
        OPERATORS = [AND, OR]

    class SIMPLE_OPERATORS:
        """
        List of simple operators handled in Contacthub
        """
        EQUALS = 'EQUALS'
        NOT_EQUALS = 'NOT_EQUALS'
        GT = 'GT'
        GTE = 'GTE'
        LT = 'LT'
        LTE = 'LTE'
        IN = 'IN'
        NOT_IN = 'NOT_IN'
        IS_NULL = 'IS_NULL'
        IS_NOT_NULL = 'IS_NOT_NULL'
        BETWEEN = 'BETWEEN'

        OPERATORS = [EQUALS, NOT_EQUALS, GT, GTE, LT, LTE, IN, NOT_IN, IS_NULL, IS_NOT_NULL, BETWEEN]

    def __init__(self, first_element, operator, second_element=None):
        """
        :param first_element:the attribute where to apply the query, an EntityField element if the criteria has a simple
        operator, another Criteria otherwise
        :param operator: an operator, simple or complex, for querying data
        :param second_element: a value, a list of value to fetch in data if the criteria has a simple operator, another
            Criteria otherwise
        """
        self.first_element = first_element
        self.operator = operator
        self.second_element = second_element

    def __and__(self, criterion):
        """
        Handling the and operation for criteria, creating a new criteria with complex operator AND

        :param criterion: a Criterion object to set in AND with this one
        :return: a new Criterion object with AND operator
        """
        return Criterion(self, Criterion.COMPLEX_OPERATORS.AND, criterion)

    def __or__(self, criterion):
        """
        Handling the or operation for criteria, creating a new criteria with complex operator OR

        :param criterion:  a Criterion object to set in OR with this one
        :return: a new Criterion object with OR operator
        """
        return Criterion(self, Criterion.COMPLEX_OPERATORS.OR, criterion)
