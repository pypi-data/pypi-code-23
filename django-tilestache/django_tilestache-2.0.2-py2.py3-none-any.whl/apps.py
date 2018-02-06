# -*- coding: utf-8
from django.apps import AppConfig


class DjangoTilestacheConfig(AppConfig):
    name = 'django_tilestache'

    def ready(self):
        from .settings import DjangoTilestacheSettings  # noqa
