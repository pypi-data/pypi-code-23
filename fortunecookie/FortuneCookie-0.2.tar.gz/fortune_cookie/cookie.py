# cookie.py

from . import phrases
from random import shuffle, choice


def fortune():

    shuffle(phrases)
    return choice(phrases)
