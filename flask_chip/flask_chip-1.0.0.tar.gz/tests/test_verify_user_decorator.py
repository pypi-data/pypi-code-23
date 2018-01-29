# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,redefined-outer-name,invalid-name

import json
import pytest

from flask import jsonify, g
from flask.views import MethodView
from six.moves import http_client as http

from flask_chip.decorators import create_verify_user
from flask_chip.tokens import generate


verify_user = create_verify_user(lambda data: data)


@pytest.fixture
def data():

    return {'pk': 'fooBarBAZ1234567890'}


@pytest.fixture
def token(data, config):
    return generate(data, config['SECRET_KEY'])


@pytest.fixture
def resource(app):

    class TestAPI(MethodView):
        @verify_user
        def get(self):  # pylint: disable=no-self-use
            return jsonify(data=g.user), http.OK  # pylint: disable=no-member

    app.add_url_rule('/test', view_func=TestAPI.as_view('test'))

    return app


def test_returns_status_ok(client, data, resource, token):  # pylint: disable=unused-argument
    response = client.get(
        '/test',
        content_type='application/json',
        headers={
            'X-Auth-Token': token,
        }
    )

    response_data = json.loads(response.get_data(as_text=True))

    assert response.status_code == http.OK  # pylint: disable=no-member
    assert response_data['data'] == data


def test_returns_unauthorized(client, resource):  # pylint: disable=unused-argument
    rv = client.get(
        '/test',
        content_type='application/json',
        headers={
            'X-Auth-Token': '',
        }
    )

    response_data = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == http.UNAUTHORIZED  # pylint: disable=no-member
    assert response_data['message'] == 'Unauthorized'
    assert response_data['status'] == http.UNAUTHORIZED  # pylint: disable=no-member
