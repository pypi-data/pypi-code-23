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

from oslo_policy import policy

from vitrage.common.policies import base

rules = [
    policy.DocumentedRuleDefault(
        name='get rca',
        check_str=base.UNPROTECTED,
        description='Show the root cause analysis on an alarm',
        operations=[
            {
                'path': '/rca',
                'method': 'GET'
            }
        ]
    ),
    policy.DocumentedRuleDefault(
        name='get rca:all_tenants',
        check_str=base.ROLE_ADMIN,
        description='Show the root cause analysis on an alarm. Include alarms'
                    ' of all tenants (if the user has the permisions)',
        operations=[
            {
                'path': '/rca',
                'method': 'GET'
            }
        ]
    )
]


def list_rules():
    return rules
