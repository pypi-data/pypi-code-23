# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pecan


class VersionsController(object):

    @staticmethod
    @pecan.expose('json')
    def index():
        return {
            'versions': [
                {
                    'status': 'CURRENT',
                    'links': [
                        {
                            'rel': 'self',
                            'href': pecan.request.application_url + '/v1/'
                        }
                    ],
                    'id': 'v1.0',
                    'updated': '2015-11-29'
                }
            ]
        }
