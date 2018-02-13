from __future__ import unicode_literals

from django.apps import AppConfig


class ApolloConfig(AppConfig):
    name = 'apollo'

    def ready(self):
        super(ApolloConfig, self).ready()
        import signals
