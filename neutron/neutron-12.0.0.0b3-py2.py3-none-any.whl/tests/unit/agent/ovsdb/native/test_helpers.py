# Copyright 2015, Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from neutron.agent.ovsdb.native import helpers
from neutron.tests import base


CONNECTION_TO_MANAGER_URI_MAP = (
    ('unix:/path/to/file', 'punix:/path/to/file'),
    ('tcp:127.0.0.1:6640', 'ptcp:6640:127.0.0.1'),
    ('ssl:192.168.1.1:8080', 'pssl:8080:192.168.1.1'))


class TestOVSNativeHelpers(base.BaseTestCase):

    def setUp(self):
        super(TestOVSNativeHelpers, self).setUp()
        self.execute = mock.patch('neutron.agent.common.utils.execute').start()

    def test__connection_to_manager_uri(self):
        for conn_uri, expected in CONNECTION_TO_MANAGER_URI_MAP:
            self.assertEqual(expected,
                             helpers._connection_to_manager_uri(conn_uri))
