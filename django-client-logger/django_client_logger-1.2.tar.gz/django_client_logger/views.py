from django.http import HttpResponse
from django.views import View
from django_client_logger.logger import process_log_message
import logging
import json

logger = logging.getLogger(__name__)


class LogReceiver(View):
    def post(self, request, *args, **kwargs):
        session_key = request.session.session_key
        body = request.POST
        try:
            data = body.get('data')
            process_log_message(json.loads(data), session_key)
        except Exception as ex:
            logger.error('Failed to process log messages: %s, "%s"' % (
                ex, data))
        return HttpResponse('')
