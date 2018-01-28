import pytest

from .. import Rumetr


@pytest.mark.parametrize('input, expected', [
    ('0', '0.00'),
    ('1', '1.00'),
    ('1.2', '1.20'),
    ('1.20', '1.20'),
    ('1.205000', '1.20'),
    ('1.208000', '1.21'),
])
def test_rouding_decimal_numbers(input, expected):
    assert Rumetr._format_decimal(input) == expected
