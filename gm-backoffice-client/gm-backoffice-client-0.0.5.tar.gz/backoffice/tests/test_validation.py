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


def test_string_items_are_accepted_instead_of_numbers_because_django_deals_correctly_with_it_and_i_dont_wont_to_fucken_mess_with_this_javascript_types(backoffice):
    assert backoffice.validate_items([
        {
            'product': {
                'site_id': '100500',
            },
            'price': '1005.05',
        },
    ]) is True


def test_invalid_item_set(backoffice):
    with pytest.raises(BackofficeValidationError) as e:
        backoffice.validate_items([
            {
                'quant1ty': 100500,
            },
        ])

        assert "name" in str(e)
