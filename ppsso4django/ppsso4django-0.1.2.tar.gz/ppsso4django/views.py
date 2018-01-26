#coding:utf-8
"""CAS login/logout replacement views"""

from urllib.parse import urlencode, urljoin

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

__all__ = ['login', 'logout']


def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """

    next_page = request.GET.get(REDIRECT_FIELD_NAME)
    if not next_page:
        if settings.CAS_IGNORE_REFERER:
            next_page = settings.CAS_REDIRECT_URL
        else:
            next_page = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] +
                  request.get_host())
        if next_page.startswith(prefix):
            next_page = next_page[len(prefix):]
    return next_page


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        url += '?' + urlencode({'service': protocol + host + next_page})
    return url


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""

    if not next_page:
        next_page = _redirect_url(request)
    if request.user.is_authenticated:
        message = "You are logged in as %s." % request.user.username
        request.user.message_set.create(message=message)
        return HttpResponseRedirect(next_page)
    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(ticket=ticket, service=service)
        if user is not None:
            auth.login(request, user)
            name = user.first_name or user.username
            message = "Login succeeded. Welcome, %s." % name
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(_login_url(service))
        else:
            error = "<h1>Forbidden</h1><p>Login failed.</p>"
            return HttpResponseForbidden(error)
    else:
        return HttpResponseRedirect(_login_url(service))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    # for pp sso start #
    if not next_page:
        next_page = _redirect_url(request)
    logout_url = _logout_url(request, next_page)
    from django.contrib.auth import logout
    logout(request)
    return HttpResponseRedirect(logout_url)
    # for pp sso end #
