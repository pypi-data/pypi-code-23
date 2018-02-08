from django.views.generic import View
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import json

from . import MC2PClient
from .signals import notification_received


class MC2PNotifyView(View):
    """
    View to receive notification
    """
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MC2PNotifyView, self).dispatch(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        body_content = request.body.decode('utf-8')
        json_body = json.loads(body_content)

        mc2p = MC2PClient()
        notification_data = mc2p.NotificationData(json_body)
        notification_received.send(sender=notification_data)

        return HttpResponse('OK')
