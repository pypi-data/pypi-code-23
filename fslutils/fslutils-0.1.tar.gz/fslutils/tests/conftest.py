""" Fixtures for use with pytest
"""

from os.path import join as pjoin, dirname

import pytest

DATA_DIR = pjoin(dirname(__file__), 'data')
BART_PUMPS = pjoin(DATA_DIR, 'bart_pumps.txt')


@pytest.fixture
def bart_pumps():
    pumps = []
    with open(BART_PUMPS, 'rt') as fobj:
        for line in fobj:
            pumps.append(float(line.split('\t')[1]))
    return pumps


@pytest.fixture
def sub_nos():
    nos = list(range(1, 30))
    for missing in (8, 15, 19, 22, 27):
        nos.remove(missing)
    return nos
