from contacthub.models.query.criterion import Criterion


def in_(value, list_attribute):
    """
    IN operation for check if a value is in a list attribute

    :param value: the value to check if is in the given list
    :param list_attribute: a list attribute for checking the presence of the value
    :return: a new Criterion object representing the IN operation between a list and a value
    """
    return Criterion(list_attribute, Criterion.SIMPLE_OPERATORS.IN, value)


def not_in_(value, list_attribute):
    """
    NOT IN operation for check if a value is NOT in a list attribute
    
    :param value: the value to check if is not in the given list
    :param list_attribute: a list attribute for checking the absence of the value
    :return: a new Criterion object representing the NOT IN operation between a list and a value
    """
    return Criterion(list_attribute, Criterion.SIMPLE_OPERATORS.NOT_IN, value)


def between_(attribute, value1, value2):
    """
    In operation for check if a str representing a date or a datetime object is between value1 and value2

    :param attribute: a date attribute to check if is between two values
    :param value1: the the lower extreme for compare the date attribute
    :param value2: the the upper extreme for compare the date attribute
    :return: a new Criterion object representing the BETWEEN operation
    """
    return Criterion(attribute, Criterion.SIMPLE_OPERATORS.BETWEEN, [value1,value2])