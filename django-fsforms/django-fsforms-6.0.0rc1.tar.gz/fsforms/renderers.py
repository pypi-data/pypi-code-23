import os

from django.forms.renderers import DjangoTemplates, ROOT as FORMS_ROOT
from django.utils.functional import cached_property

ROOT = os.path.dirname(__file__)


class FoundationEngineMixin:

    @cached_property
    def engine(self):
        return self.backend({
            'APP_DIRS': True,
            'DIRS': [
                # look for widget templates in this app and
                # fall back to the Django built-in ones
                os.path.join(ROOT, self.backend.app_dirname),
                os.path.join(FORMS_ROOT, self.backend.app_dirname),
            ],
            'NAME': 'foundationforms',
            'OPTIONS': {},
        })


class DjangoTemplates(FoundationEngineMixin, DjangoTemplates):
    """
    Load Django templates from the 'templates' directory of this
    app, the built-in widget templates in django/forms/templates
    and from apps' 'templates' directory.
    """
