"""This module contains support functions and classes for other modules."""


def is_better(ori_value, comparing_value, is_greater):
    """
    This module compare the two values based on what we are looking for
    (Min or Max).

    :param ori_value: Original value.
    :type ori_value: number
    :param comparing_value: New value to compare with.
    :type comparing_value: number
    :param is_greater: True if you want to know b > a, else False if you want
    to check b < a.
    :return: If b is better than a or not.
    :rtype: bool
    """

    if ori_value is not None:
        if (is_greater and comparing_value <= ori_value) or \
                (not is_greater and comparing_value >= ori_value):
            return False
    return True
