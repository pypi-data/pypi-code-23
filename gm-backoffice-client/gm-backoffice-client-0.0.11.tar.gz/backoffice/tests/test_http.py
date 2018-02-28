import pytest
import requests_mock

from ..client import BackofficeHTTPException


def test_authorization_headers(backoffice):
    assert backoffice.headers['Authorization'] == 'Token tsttkn', 'corrrect token is inserted within __init__'


def test_order_url(backoffice):
    with requests_mock.mock() as m:
        m.post('http://testhost/orders/', status_code=201, json={'mock': 'mmmock'})
        assert backoffice.post_order('some stuff') == {'mock': 'mmmock'}


def test_non_201_response_to_order_post(backoffice):
    with requests_mock.mock() as m:
        m.post('http://testhost/orders/', status_code=403)
        with pytest.raises(BackofficeHTTPException):
            backoffice.post_order('some stuff')


def test_items_url(backoffice):
    with requests_mock.mock() as m:
        m.post('http://testhost/orders/100500/items/', status_code=201, json={'mock': 'mmmock'})
        assert backoffice.post_items({'id': 100500}, [{'mo': 'ck'}]) == {'mock': 'mmmock'}


def test_non_201_response_to_items_post(backoffice):
    with requests_mock.mock() as m:
        m.post('http://testhost/orders/100500/items/', status_code=403)
        with pytest.raises(BackofficeHTTPException):
            backoffice.post_items({'id': 100500}, [{'mo': 'ck'}])


@pytest.mark.parametrize('api_data', (
    {
        'price_cashless': '300500.00',
        'price_cash': '200500.00',
    },
))
def test_price_url(api_data, backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/price_lists/sell/100500/', status_code=200, json=api_data)

        assert backoffice.get_price(100500) == api_data


def test_non_200_response_to_price_get(backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/price_lists/sell/100500/', status_code=404)

        with pytest.raises(BackofficeHTTPException):
            assert backoffice.get_price(100500)


@pytest.mark.parametrize('api_data', (
    [
        {
            'id': 100,
            'site_id': 128,
            'name': 'Коробка с функциональными языками',
            'orders_count': 450,
        },
        {
            'id': 234,
            'site_id': 256,
            'name': 'Пакет с лиспами',
            'orders_count': 4,
        },
    ],
))
def test_product_sales_stat_url(api_data, backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/products/sales_stat/?site_ids=128,256', status_code=200, json=api_data)

        assert backoffice.get_products_sales_stat([128, 256]) == api_data


def test_non_200_response_to_product_sales_stat_get(backoffice):
    with requests_mock.mock() as m:
        m.get('http://testhost/products/sales_stat/?site_ids=128,256', status_code=404)

        with pytest.raises(BackofficeHTTPException):
            assert backoffice.get_products_sales_stat([128, 256])
