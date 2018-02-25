import json
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import DisallowedRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse
from django.utils.encoding import force_text, iri_to_uri


class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(self, data=None, encoder=DjangoJSONEncoder, safe=True,
                 json_dumps_params=None, include_status=None,
                 always_http_ok=None, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(**kwargs)

        if data is None:
            data = {}
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if include_status is None:
            include_status = getattr(settings, 'JSON_INCLUDE_STATUS', False)
        if always_http_ok is None:
            always_http_ok = getattr(settings, 'JSON_ALWAYS_HTTP_OK', False)
        status_field = getattr(settings, 'JSON_STATUS_FIELD', 'status')
        reason_field = getattr(settings, 'JSON_REASON_FIELD', 'reason')
        reason_on_error = getattr(settings, 'JSON_REASON_ON_ERROR', True)
        if json_dumps_params is None:
            json_dumps_params = {}
        if isinstance(data, dict):
            if include_status:
                data.setdefault(status_field, self.status_code)
            if include_status or (self.status_code != 200 and reason_on_error):
                data.setdefault(reason_field, self.reason_phrase)
        if always_http_ok:
            self.status_code = 200
        self.content = json.dumps(data, cls=encoder, **json_dumps_params)


class JsonResponseRedirectBase(JsonResponse):
    allowed_schemes = ['http', 'https', 'ftp']

    def __init__(self, redirect_to, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['Location'] = iri_to_uri(redirect_to)
        parsed = urlparse(force_text(redirect_to))
        if parsed.scheme and parsed.scheme not in self.allowed_schemes:
            raise DisallowedRedirect("Unsafe redirect to URL with protocol '%s'" % parsed.scheme)

    url = property(lambda self: self['Location'])

    def __repr__(self):
        return '<%(cls)s status_code=%(status_code)d%(content_type)s, url="%(url)s">' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
            'url': self.url,
        }


class JsonResponsePermanentRedirect(JsonResponseRedirectBase):
    status_code = 301


class JsonResponseRedirect(JsonResponseRedirectBase):
    status_code = 302


class JsonResponseBadRequest(JsonResponse):
    status_code = 400


class JsonResponseUnauthorized(JsonResponse):
    status_code = 401


class JsonResponseForbidden(JsonResponse):
    status_code = 403


class JsonResponseNotFound(JsonResponse):
    status_code = 404


class JsonResponseNotAllowed(JsonResponse):
    status_code = 405

    def __init__(self, permitted_methods, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['Allow'] = ', '.join(permitted_methods)

    def __repr__(self):
        return '<%(cls)s [%(methods)s] status_code=%(status_code)d%(content_type)s>' % {
            'cls': self.__class__.__name__,
            'status_code': self.status_code,
            'content_type': self._content_type_for_repr,
            'methods': self['Allow'],
        }


class JsonResponseGone(JsonResponse):
    status_code = 410


class JsonResponseServerError(JsonResponse):
    status_code = 500
