from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from molo.core.tests.base import MoloTestCaseMixin


class TemplateTagsTestCase(TestCase, MoloTestCaseMixin):
    def render_template(self, template_string, context):
        return Template(template_string).render(Context(context))

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = AnonymousUser()

    def test_template_renders_without_error(self):
        template = self.render_template(
            '{% load molo_pwa %} {% molo_pwa_meta %}',
            {
                'request': self.request,
            },
        )
        self.assertIn('<link rel="manifest" href="/manifest.json">', template)

    def test_template_no_fcm_config_if_user_anonymous(self):
        template = self.render_template(
            '{% load molo_pwa %} {% molo_pwa_meta %}',
            {
                'request': self.request,
            },
        )
        self.assertNotIn('fcmConfig', template)

    def test_template_has_fcm_config_if_user_authed(self):
        self.mk_main()
        user = get_user_model().objects.create()
        self.request.user = user
        template = self.render_template(
            '{% load molo_pwa %} {% molo_pwa_meta %}',
            {
                'request': self.request,
            },
        )
        self.assertIn('fcmConfig', template)
