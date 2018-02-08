import os

import six
from django.conf import settings
from django.utils.module_loading import import_string

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_SETTINGS = getattr(settings, 'OCTO_DRF', None)

default_auth_handler = 'octo_drf.apps.auth.handlers.default_auth_handler'

DEFAULTS = {
    # Обработчики респонса для функций модуля auth. Функция должа принимать объект request и вовзращать объект типа dict
    'auth': {
        'register_handler': default_auth_handler,
        'register_confirm_handler': default_auth_handler,
        'login_handler': default_auth_handler,
        'reset_password_confirm_handler': default_auth_handler,
        'reset_password_inplace_handler': default_auth_handler
    },
    'base_siteconfig': {
        'fields_to_translate': []
    },
    'gallery': {
        'fields_to_translate': []
    },
    'static_blocks': {
        'fields_to_translate': []
    },
    'widgets': {
        'fields_to_translate': {
            'CoreWidgetType': [],
            'CoreWidget': []
        }
    },
    'logging': {
        'subs': []
    },
    'caching': {
        'map': ''
    }
}


class ProjectSettings:
    # TODO: рефактор _perform_import чтобы в settings можно было записывать не только функции

    def __init__(self, defaults, users=None):
        if users:
            self.settings = self._compare_settings(defaults, users)
        else:
            self.settings = defaults

    def __getitem__(self, item):
        return self._perform_import(self.settings[item])

    def _perform_import(self, val):
        if isinstance(val, dict):
            return ProjectSettings(val)
        elif isinstance(val, six.string_types):
            return import_string(val)
        return val

    def _compare_settings(self, defaults, user):
        """
        Parse and replace user octo_drf settings
        """
        for k in defaults:
            if k in user:
                for internal_key in user[k]:
                    defaults[k][internal_key] = user[k][internal_key]
        return defaults


if USER_SETTINGS:
    project_settings = ProjectSettings(DEFAULTS, USER_SETTINGS)
else:
    project_settings = ProjectSettings(DEFAULTS)
