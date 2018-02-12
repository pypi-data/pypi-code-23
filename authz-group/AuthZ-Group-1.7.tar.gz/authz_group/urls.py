from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'authz_group.views.demo_page'),
    url(r'^/rest/v1/groups$', 'authz_group.views.group_data'),
]
