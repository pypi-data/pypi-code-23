#!usr/bin/env python

def factorial(n):
    """
    This function calculates the factorial of a given number n.

    parameters
    ----------
    n: an integer you want to calculate the factorial af

    returns
    -------
    The factorial of the number you just provided

    examples
    --------
    >>> factorial(4)
    24
    >>> factorial(5)
    120
    >>> factorial(6)
    720
    """
    n = int(n)
    fact = 1
    while n!= 0:
        fact *= n
        n -= 1
    return fact

def fibonnaci(a,b,n):
    """
    This function gives a general Fibonnaci series of size n.

    parameters
    ----------
    a: a first real number
    b: a second real number
    n: the size of the Fibonnaci series

    returns
    -------
    A general Fibonnaci series starting from two provided real numbers.

    examples
    --------
    >>> fibonnaci(1,1,10)
    1, 1, 2, 3, 5, 8, 13, 21, 34, 55
    >>> fibonacci(2,2,10)
    2, 2, 4, 6, 10, 16, 26, 42, 68, 110
    """
    series = [int(a),int(b)]
    while n!= 0:
        series.append(series[-2]+series[-1])
        n -=1
    return ', '.join(series)
