# -*- coding: utf-8
from django.apps import apps, AppConfig
from django.core.exceptions import ImproperlyConfigured


class GenomixUsersConfig(AppConfig):
    name = 'genomix_users'
    verbose_name = 'Users'

    requirements = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework.authtoken',
        'rest_auth',
        'django_python3_ldap',
    ]

    def ready(self):
        from . import signals  # noqa NOTE: This is to setup signals

        for requirement in self.requirements:
            if not apps.is_installed(requirement):
                raise ImproperlyConfigured('{0} must be in INSTALLED_APPS'.format(requirement))
