# Copyright (c) 2016 Orange.
# All Rights Reserved.
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

from neutron.tests.fullstack.resources import config as neutron_cfg


class ML2ConfigFixture(neutron_cfg.ML2ConfigFixture):

    def __init__(self, env_desc, host_desc, temp_dir, tenant_network_types):
        super(ML2ConfigFixture, self).__init__(
            env_desc, host_desc, temp_dir, tenant_network_types)

        if env_desc.bagpipe_ml2:
            self.config['ml2']['type_drivers'] = 'route_target'
            self.config.update({
                'ml2_type_route_target': {
                    'rt_nn_ranges': '100:199'
                }
            })
