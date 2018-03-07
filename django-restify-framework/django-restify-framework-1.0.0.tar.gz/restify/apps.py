from django.apps import AppConfig


class RestifyConfig(AppConfig):
    name = 'restify'
    verbose_name = "Django restify"

    def ready(self):
        from restify import signals