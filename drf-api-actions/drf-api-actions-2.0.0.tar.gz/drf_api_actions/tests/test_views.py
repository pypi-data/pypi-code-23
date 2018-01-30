from django.conf.urls import include, url
from django.test import TestCase, override_settings
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_api_actions.views import ActionReadMixin, SchemaGeneratorEx


class CommonTestView(APIView):
    def get(self, request):
        return Response('')


class ActionReadTestView(ActionReadMixin, CommonTestView):
    pass


urlpatterns = [
    url('^action-read$', ActionReadTestView.as_view()),
    url('^', include('drf_api_actions.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class BaseCoreAPITest(TestCase):
    def setUp(self):
        self.generator = SchemaGeneratorEx()
        self.schema = self.generator.get_schema()


class TestActionReadMixin(BaseCoreAPITest):
    def test_action_read(self):
        self.assertIsNone(self.schema['action-read'].get('list'))
        self.assertIsNotNone(self.schema['action-read'].get('read'))
