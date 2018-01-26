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

from karborclient.common import base


class Verification(base.Resource):
    def __repr__(self):
        return "<Verification %s>" % self._info


class VerificationManager(base.ManagerWithFind):
    resource_class = Verification

    def create(self, provider_id, checkpoint_id, parameters):
        body = {
            'verification': {
                'provider_id': provider_id,
                'checkpoint_id': checkpoint_id,
                'parameters': parameters,
            }
        }
        url = "/verifications"
        return self._create(url, body, 'verification')

    def get(self, verification_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/verifications/{verification_id}".format(
            verification_id=verification_id)
        return self._get(url, response_key="verification", headers=headers)

    def list(self, detailed=False, search_opts=None, marker=None, limit=None,
             sort_key=None, sort_dir=None, sort=None):
        """Lists all verifications.

        :param detailed: Whether to return detailed verification info.
        :param search_opts: Search options to filter out verifications.
        :param marker: Begin returning verifications that appear later in the
                       list than that represented by this verification id.
        :param limit: Maximum number of verifications to return.
        :param sort_key: Key to be sorted;
        :param sort_dir: Sort direction, should be 'desc' or 'asc';
        :param sort: Sort information
        :rtype: list of :class:`Verification`
        """

        resource_type = "verifications"
        url = self._build_list_url(
            resource_type, detailed=detailed,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'verifications')
