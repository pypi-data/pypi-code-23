from argparse import ArgumentTypeError


def check_positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise ArgumentTypeError('{} is not a positive value'.format(value))
    return ivalue
