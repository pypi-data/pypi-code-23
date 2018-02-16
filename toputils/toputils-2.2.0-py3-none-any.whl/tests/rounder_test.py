
from toputils.rounder import price_rounder


def test_rounder_no_rolls():
    assert price_rounder(1.9, 0) == 1.9


def test_rounder_plus_rolls():
    assert price_rounder(1.9, 5) == 1.85


def test_rounder_minus_rolls():
    assert price_rounder(1.9, -5) == 1.95


def test_rounder_price_over_501():
    assert price_rounder(513.5753720394616) == 501


def test_rounder_price_near_zero():
    assert price_rounder(0.1) == 0


def test_rounder_price_negative():
    assert price_rounder(-0.1) == 0


def test_rounder_price_over_501_with_negative_rolls():
    assert price_rounder(513, -1) == 501


def test_rounder_price_401_with_negative_rolls():
    assert price_rounder(601, -1) == 501
    assert price_rounder(401, -2) == 501
    assert price_rounder(401, -3) == 501
    assert price_rounder(401, -4) == 501


def test_above_rolls_range_with_positive_rolls():
    assert price_rounder(601, 1) == 501


def test_above_rolls_range_with_positive_rolls_1():
    assert price_rounder(601, 4) == 301


def test_rolls_on_max_div_returns_zero():
    assert price_rounder(5001, -1) == 0


def test_1_returns_1():
    assert price_rounder(1) == 1


def test_pt95_returns_1():
    assert price_rounder(0.95) == 1
