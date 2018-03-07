from django.conf.urls import include, url

from restify.api import Api
from tests.resources.test_model import PersonResource, PersonSetResource

api = Api(api_name='v1')
api.register(regex='person/(?P<pk>\d+|new)/$', resource=PersonResource)
api.register(regex='persons/$', resource=PersonSetResource)

urlpatterns = [
    url(r'^api/', include((api.urls, 'api'), namespace='api')),
]
