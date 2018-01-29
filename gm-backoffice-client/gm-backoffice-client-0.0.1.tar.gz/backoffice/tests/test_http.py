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
