import pytest

from .. import processors


def test_order_date_processor_is_present_in_the_order_processors_list(backoffice):
    assert processors.p01_format_date in list(backoffice.get_processors('order'))


def test_order_date_processor_is_not_present_in_the_item_processors_list(backoffice):
    assert processors.p01_format_date not in list(backoffice.get_processors('items'))


def test_order_date_processor_is_ran(backoffice):
    order = {
        'delivery': {
            'desired_date': '30.09.2019',
        },
    }
    assert backoffice.run_processors(order, 'order') == {
        'delivery': {
            'desired_date': '2019-09-30',
        },
    }


def test_incorrect_desired_date_is_dropped(backoffice):
    order = {
        'delivery': {
            'desired_date': 'unp4rs4ble',
        },
    }
    assert backoffice.run_processors(order, 'order') == {}


@pytest.mark.parametrize('input, expected', [
    ('30.09.2019', '2019-09-30'),
    ('2019-09-30', '2019-09-30'),
    ('2017', None),
    ('2017-15-11 12:48', None),
    ('12.12.2017 12:48', None),
    ('12..2016', None),
    ('12....2016', None),
])
def test_desired_date_processing(input, expected):
    order = {
        'delivery': {
            'desired_date': input,
        },
    }
    assert processors.p01_format_date(order) == {
        'delivery': {
            'desired_date': expected,
        },
    }


def test_order_without_desired_date_does_not_break_things():
    order = {
        'delivery': {
        },
    }
    assert processors.p01_format_date(order) == order


def test_order_without_delivery_object_does_not_break_things():
    order = {
    }
    assert processors.p01_format_date(order) == order


def test_drop_keys_without_values():
    d = {
        'with_value': '100500',
        'integer_value_that_should_stay': 0,
        'wihout_value': '',
        'wihout_value_1': None,
        'empty_list_that_should_be_deleted_either': [],

        'subdict_with_values': {
            'with_value': '100500',
            'wihout_value': None,
        },

        'subdict_without_values': {
            'woihout_value': None,
        },

        'subdict_with_subdicts_wihout_values': {
            'subdict_without_values': {
                'wohtout_vaue': None,
            },
        },
    }

    assert processors.p99_drop_keys_without_values(d) == {
        'with_value': '100500',
        'integer_value_that_should_stay': 0,
        'subdict_with_values': {
            'with_value': '100500',
        },
    }
