from django.http.response import HttpResponse
from django.views.generic.base import View


settings = None


# TODO: Maybe move this outside
# Lazy get settings
def get_settings():
    global settings
    if not settings:
        from django import conf
        settings = conf.settings
    return settings


class StatusView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')


class DBStatusView(View):
    def get(self, request, *args, **kwargs):
        django_settings = get_settings()
        status = {
            'setup': False,
        }
        dbs = getattr(django_settings, 'DATABASES')
        if dbs:
            status['setup'] = True
            status['count'] = len(dbs)

        response = ''
        for key, value in status.items():
            response += f'{key}: {value}<br>\n'
        return HttpResponse(response)
