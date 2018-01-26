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

from openstack_dashboard.dashboards.project.cgroups import views


urlpatterns = [
    url(r'^$', views.CGroupsView.as_view(), name='index'),
    url(r'^create/$',
        views.CreateView.as_view(),
        name='create'),
    url(r'^(?P<cgroup_id>[^/]+)/update/$',
        views.UpdateView.as_view(),
        name='update'),
    url(r'^(?P<cgroup_id>[^/]+)/remove_volumese/$',
        views.RemoveVolumesView.as_view(),
        name='remove_volumes'),
    url(r'^(?P<cgroup_id>[^/]+)/delete/$',
        views.DeleteView.as_view(),
        name='delete'),
    url(r'^(?P<cgroup_id>[^/]+)/manage/$',
        views.ManageView.as_view(),
        name='manage'),
    url(r'^(?P<cgroup_id>[^/]+)/create_snapshot/$',
        views.CreateSnapshotView.as_view(),
        name='create_snapshot'),
    url(r'^(?P<cgroup_id>[^/]+)/clone_cgroup/$',
        views.CloneCGroupView.as_view(),
        name='clone_cgroup'),
    url(r'^(?P<cgroup_id>[^/]+)$',
        views.DetailView.as_view(),
        name='detail'),
]
