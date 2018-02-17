from django.apps import AppConfig

class MyAppConfig(AppConfig):

    name = 'page'
    verbose_name = 'Page'

    def ready(self):
        import page.signals