from django.template.backends.django import DjangoTemplates

from bureaucracy.powerpoint.engines import BaseEngine


class DjangoSlideEngine(BaseEngine):

    def __init__(self, extra_builtins=None):
        extra_builtins = extra_builtins or []

        options = {
            'NAME': '',
            'OPTIONS': {
                'builtins': ['django_bureaucracy.templatetags', ] + extra_builtins

            },
            'DIRS': [],
            'APP_DIRS': True
        }

        self.django_tpls = DjangoTemplates(options)

    def render(self, fragment, context):
        fragment = '{{% autoescape off %}}{fragment}{{% endautoescape %}}'.format(fragment=fragment)
        tpl = self.django_tpls.from_string(fragment)
        return tpl.render(context)
