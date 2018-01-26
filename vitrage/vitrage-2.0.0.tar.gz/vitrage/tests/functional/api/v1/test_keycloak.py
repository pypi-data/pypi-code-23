# Copyright 2017 - Nokia Corporation
# Copyright 2014 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# noinspection PyPackageRequirements
from datetime import datetime
from mock import mock
import requests_mock
from vitrage.middleware.keycloak import KeycloakAuth
from vitrage.tests.functional.api.v1 import FunctionalTest
from webtest import TestRequest


TOKEN = {
    "iss": "http://127.0.0.1/auth/realms/my_realm",
    "realm_access": {
        "roles": ["role1", "role2"]
    }
}

HEADERS = {
    'X-Auth-Token': str(TOKEN),
    'X-Project-Id': 'my_realm'
}

OPENID_CONNECT_USERINFO = 'http://127.0.0.1:9080/auth/realms/my_realm/' \
                          'protocol/openid-connect/userinfo'

USER_CLAIMS = {
    "sub": "248289761001",
    "name": "Jane Doe",
    "given_name": "Jane",
    "family_name": "Doe",
    "preferred_username": "j.doe",
    "email": "janedoe@example.com",
    "picture": "http://example.com/janedoe/me.jpg"
}

EVENT_DETAILS = {
    'hostname': 'host123',
    'source': 'sample_monitor',
    'cause': 'another alarm',
    'severity': 'critical',
    'status': 'down',
    'monitor_id': 'sample monitor',
    'monitor_event_id': '456',
}

NO_TOKEN_ERROR_MSG = {'error': {
    'code': 401,
    'title': 'Unauthorized',
    'message': 'Auth token must be provided in "X-Auth-Token" header.',
}}


class KeycloakTest(FunctionalTest):

    def __init__(self, *args, **kwds):
        super(KeycloakTest, self).__init__(*args, **kwds)
        self.auth = 'keycloak'

    @staticmethod
    def _build_request():
        req = TestRequest.blank('/')
        req.headers = HEADERS
        return req

    @mock.patch('jwt.decode', return_value=TOKEN)
    @requests_mock.Mocker()
    def test_header_parsing(self, _, req_mock):

        # Imitate success response from KeyCloak.
        req_mock.get(OPENID_CONNECT_USERINFO)

        req = self._build_request()
        auth = KeycloakAuth(mock.Mock(), self.CONF)
        auth.process_request(req)

        self.assertEqual('Confirmed', req.headers['X-Identity-Status'])
        self.assertEqual('my_realm', req.headers['X-Project-Id'])
        self.assertEqual('role1,role2', req.headers['X-Roles'])
        self.assertEqual(1, req_mock.call_count)

    def test_in_keycloak_mode_no_token(self):
        resp = self.post_json('/topology/', expect_errors=True)

        self.assertEqual('401 Unauthorized', resp.status)
        self.assertEqual(NO_TOKEN_ERROR_MSG, resp.json)

    @mock.patch('jwt.decode', return_value=TOKEN)
    @requests_mock.Mocker()
    def test_in_keycloak_mode_wrong_token(self, _, req_mock):

        # Imitate failure response from KeyCloak.
        req_mock.get(
            requests_mock.ANY,
            status_code=401,
            reason='Access token is invalid'
        )

        resp = self.post_json('/topology/',
                              params=None,
                              headers=HEADERS,
                              expect_errors=True)

        self.assertEqual('401 Unauthorized', resp.status)

    @mock.patch('jwt.decode', return_value=TOKEN)
    @requests_mock.Mocker()
    def test_in_keycloak_mode_auth_success(self, _, req_mock):

        # Imitate success response from KeyCloak.
        req_mock.get(OPENID_CONNECT_USERINFO, json=USER_CLAIMS)

        with mock.patch('pecan.request') as request:
            resp = self.post_json('/event/',
                                  params={
                                      'time': datetime.now().isoformat(),
                                      'type': 'compute.host.down',
                                      'details': EVENT_DETAILS
                                  },
                                  headers=HEADERS)

            self.assertEqual(1, request.client.call.call_count)
            self.assertEqual('200 OK', resp.status)
