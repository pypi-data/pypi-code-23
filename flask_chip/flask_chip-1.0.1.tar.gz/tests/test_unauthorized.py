# -*- coding: utf-8 -*-

import json

from six.moves import http_client as http

from flask_chip.utils import unauthorized


def test_call_response_with_401_and_message_as_json():
    result = unauthorized()

    data = json.loads(result.get_data().decode('utf-8'))

    assert result.status_code == http.UNAUTHORIZED
    assert data['status'] == http.UNAUTHORIZED
    assert data['message'] == 'Unauthorized'
