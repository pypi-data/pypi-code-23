from django.http import HttpResponse
from health_check.views import MainView

class HealthCheckCustomView(MainView):

    def render_to_response(self, plugin, status):
        return HttpResponse('pong' if status == 200 else 'sweaty', status=status)
