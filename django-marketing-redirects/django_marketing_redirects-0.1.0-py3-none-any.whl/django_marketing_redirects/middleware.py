from collections import OrderedDict

from django.conf import settings
from django.contrib.redirects import middleware as redirects_middleware
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site

try:
    # python 2
    import urlparse
except ModuleNotFoundError:
    # python 3
    import urllib.parse as urlparse


class RedirectFallbackMiddleware(redirects_middleware.RedirectFallbackMiddleware):

    def process_response(self, request, response):
        # No need to check for a redirect for non-404 responses.
        if response.status_code != 404:
            return response

        full_path = request.get_full_path()
        current_site = get_current_site(request)

        request_path = urlparse.urlsplit(full_path)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=full_path)
        except Redirect.DoesNotExist:
            try:
                r = Redirect.objects.get(site=current_site, old_path=request_path.path)
            except Redirect.DoesNotExist:
                pass
        if r is None and settings.APPEND_SLASH and not request.path.endswith('/'):
            try:
                r = Redirect.objects.get(
                    site=current_site,
                    old_path=request.get_full_path(force_append_slash=True),
                )
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == '':
                return self.response_gone_class()
            if hasattr(r, 'redirectwithqueryparams'):
                behavior = r.redirectwithqueryparams.query_param_behavior
                request_params = OrderedDict(urlparse.parse_qsl(request_path.query))
                request_path = urlparse.urlsplit(r.new_path)
                response_params = OrderedDict(urlparse.parse_qsl(request_path.query))
                if behavior == 'REMOVE':
                    params = {}
                elif behavior == 'REDIRECT_WINS':
                    request_params.update(response_params)
                    params = request_params
                elif behavior == 'QUERY_WINS':
                    response_params.update(request_params)
                    params = response_params
                if len(params) > 0:
                    return self.response_redirect_class(request_path.path + '?' + urlparse.urlencode(params))
            return self.response_redirect_class(r.new_path)

        # No redirect was found. Return the response.
        return response
