from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class PluginApp(AppConfig):
    name = 'pretix_mabel'
    verbose_name = 'Pretix Mabel'

    class PretixPluginMeta:
        name = ugettext_lazy('Pretix Mabel')
        author = 'Christopher Little'
        description = ugettext_lazy('Pretix customised for use at May Balls')
        visible = True
        version = '1.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_mabel.PluginApp'
