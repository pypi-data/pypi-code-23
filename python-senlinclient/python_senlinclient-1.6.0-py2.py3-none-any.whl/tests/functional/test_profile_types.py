# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from senlinclient.tests.functional import base


class ProfileTypeTest(base.OpenStackClientTestBase):
    """Test for profile types

    Basic smoke test for the Openstack CLI commands which do not require
    creating or modifying.
    """
    def test_profile_type_list(self):
        result = self.openstack('cluster profile type list')
        profile_type = self.parser.listing(result)
        self.assertTableStruct(profile_type, ['name', 'version',
                                              'support_status'])

    def test_profile_list_debug(self):
        self.openstack('cluster profile list', flags='--debug')

    def test_profile_type_show(self):
        params = ['container.dockerinc.docker-1.0',
                  'os.heat.stack-1.0',
                  'os.nova.server-1.0']
        for param in params:
            cmd = 'cluster profile type show %s' % param
            self.openstack(cmd)

    def test_profile_type_show_json(self):
        self.openstack('cluster profile type show os.nova.server-1.0 -f json')
