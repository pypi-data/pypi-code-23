# Copyright 2012 NEC Corporation
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

from openstack_dashboard.dashboards.project.networks.ports \
    import tabs as project_tabs
from openstack_dashboard.dashboards.project.networks.ports.extensions. \
    allowed_address_pairs import tabs as addr_pairs_tabs


class OverviewTab(project_tabs.OverviewTab):
    template_name = "project/networks/ports/_detail_overview.html"


class PortDetailTabs(project_tabs.PortDetailTabs):
    tabs = (OverviewTab, addr_pairs_tabs.AllowedAddressPairsTab)
