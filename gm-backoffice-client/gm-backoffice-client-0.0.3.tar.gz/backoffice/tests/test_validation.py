import pytest

from ..client import BackofficeValidationError


def test_valid_order(backoffice):
    assert backoffice.validate_order({
        'customer': {
            'name': 'Petrovich',
        },
    }) is True


def test_invalid_order(backoffice):
    with pytest.raises(BackofficeValidationError) as e:
        backoffice.validate_order({})

        assert "customer" in str(e)


def test_valid_item_set(backoffice):
    assert backoffice.validate_items([
        {
            'product': {
                'name': 'kamaz of ships',
            },
        },
    ]) is True


def test_invalid_item_set(backoffice):
    with pytest.raises(BackofficeValidationError) as e:
        backoffice.validate_items([
            {
                'product': {
                },
                'quant1ty': 100500,
            },
        ])

        assert "name" in str(e)
