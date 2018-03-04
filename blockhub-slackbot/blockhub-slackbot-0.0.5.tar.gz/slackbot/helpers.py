import re


def listify(string):
    """
    :param string:
    :return: list of space separated words of string input
    """
    return re.sub("[^\w]", " ",  string).split()

