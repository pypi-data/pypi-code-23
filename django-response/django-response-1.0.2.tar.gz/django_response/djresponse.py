# -*- coding: utf-8 -*-

try:
    from django.http import JsonResponse
except ImportError:
    from json_response import JsonResponse
from StatusCode import StatusCodeField


def response_data(status_code=200, message=None, description=None, data={}, **kwargs):
    return dict({
        'status': status_code,
        'message': message,
        'description': description,
        'data': data,
    }, **kwargs)


def response(status_code=200, message=None, description=None, data={}, msg_args=[], msg_kwargs={}, desc_args=[], desc_kwargs={}, **kwargs):
    message, description = (message or status_code.message, description or status_code.description) if isinstance(status_code, StatusCodeField) else (message, description)
    return JsonResponse(response_data(status_code, (message or '').format(*msg_args, **msg_kwargs), (description or '').format(*desc_args, **desc_kwargs), data, **kwargs), safe=False)
