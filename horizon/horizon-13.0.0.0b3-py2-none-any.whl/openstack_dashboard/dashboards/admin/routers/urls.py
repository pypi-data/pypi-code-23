# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
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

from django.conf.urls import url

from openstack_dashboard.dashboards.admin.routers import views


ROUTER_URL = r'^(?P<router_id>[^/]+)/%s'


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(ROUTER_URL % '$',
        views.DetailView.as_view(),
        name='detail'),
    url(ROUTER_URL % 'update',
        views.UpdateView.as_view(),
        name='update'),
    url(r'^(?P<l3_agent_id>[^/]+)/l3_agent_list',
        views.L3AgentView.as_view(),
        name='l3_agent_list'),
]
