from collections import namedtuple

from django.conf import settings

from .request import APIMethods
from .response_utils import ApiResponse
from .session import Session


def allowed_methods(api_methods):
    """
    Decorator to make a view only accept particular request methods.  Usage::

        @require_http_methods({adhara.request.APIMethods.GET, adhara.request.APIMethods.POST})
        class XViewClass(RestView):
            # I can assume now that only GET (unique) or POST requests make it this far
            # ...

    Note that request methods should be passing a set of `adhara.request.APIMethods` types
    :param {Set<adhara.request.APIMethods>} api_methods: set of allowed Adhara API methods
    """
    all_methods = set(APIMethods)
    restricted_methods = all_methods.difference(api_methods)

    def _method_not_allowed(self):
        self._response.error({"allowed_methods": list(map(lambda x: x.value, api_methods))}, error_code=403)
        return self._response
        # pratikriyaa = {
        #     "status": "error",
        #     "data":
        # }
        # return ApiResponse.NotAllowedPratikriyaa(pratikriyaa)
        # return HttpResponseNotAllowed(list(map(lambda x:x.value, api_methods)))

    def fn(cls):
        for method in restricted_methods:
            setattr(cls, method.value.lower(), _method_not_allowed)
        return cls
    return fn


def is_logged_in(cls):
    default_dispatcher = cls.dispatch

    def auth_and_dispatch(self, request, *args, **kwargs):
        if Session.is_logged_in(request):
            return default_dispatcher(self, request, *args, **kwargs)
        else:
            return ApiResponse.error("Not Logged In")
    cls.dispatch = auth_and_dispatch
    return cls


StaticFiles = namedtuple("StaticFiles", ["CSS", "JS"])
_CSS = settings.ADHARA["CSS"] if "CSS" in settings.ADHARA else {}
_JS = settings.ADHARA["JS"] if "JS" in settings.ADHARA else {}


def _get_for_context(contexts):
    if type(contexts) is str:
        contexts = [contexts]
    css_files = []
    js_files = []
    for context in contexts:
        css_files.extend(_CSS[context])
        js_files.extend(_JS[context])
    return StaticFiles(css_files, js_files)


def include_static_contexts(contexts):
    def ret(fn):
        def req_incl_fn(request, *args, **kwargs):
            kwargs['static_files'] = _get_for_context(contexts)
            return fn(request, *args, **kwargs)
        return req_incl_fn
    return ret
