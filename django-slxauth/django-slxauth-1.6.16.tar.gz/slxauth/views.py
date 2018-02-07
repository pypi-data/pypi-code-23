import logging

import requests
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views import View
from requests.auth import HTTPBasicAuth

from slxauth.utils import get_authenticator

logger = logging.getLogger(__name__)


class LoginView(View):
    """ This is the view that django opens """
    def get(self, request):
        if not 'next' in request.GET:
            logger.debug('no next provided. this seems to be an unusual request.')
            return HttpResponseForbidden()

        next = request.GET['next']
        redirect_uri = request.build_absolute_uri('%s?next=%s' % (reverse('slxauth:callback'), next))
        authorize_url = '%s/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (
            settings.OAUTH_URL,
            settings.OAUTH_CLIENT_ID,
            redirect_uri
        )
        logger.debug('redirecting to %s' % authorize_url)
        return HttpResponseRedirect(redirect_to=authorize_url)


class CallbackView(View):
    """ This handles the callback from the OAuth2 Auth server.
    Users will be redirected to this view after successful login.
    """
    def get(self, request):
        if 'code' not in request.GET:
            logger.debug('no code provided')
            return HttpResponseForbidden()

        if 'next' not in request.GET:
            logger.debug('no next provided. this seems to be an unusual request.')
            return HttpResponseForbidden()

        code = request.GET['code']
        next = request.GET['next']

        logger.debug('received callback code %s' % code)
        redirect_uri = request.build_absolute_uri('%s?next=%s' % (reverse('slxauth:callback'), next))
        url = '%s/token?grant_type=authorization_code&code=%s&redirect_uri=%s' % (settings.OAUTH_URL, code, redirect_uri)

        logger.debug('validating code using %s' % url)

        authresponse = None

        try:
            authresponse = requests.post(
                url,
                auth=HTTPBasicAuth(settings.OAUTH_CLIENT_ID,
                                   settings.OAUTH_CLIENT_SECRET),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=0.5)

            logger.debug('response: %s' % authresponse)
            logger.debug('response content: %s' % authresponse.content)
        except Exception as e:
            logger.error('could not validate token: %s' % e)

        if authresponse and authresponse.status_code == 200:
            data = authresponse.json()

            if 'access_token' in data and 'expires_in' in data and 'refresh_token' in data:
                access_token = data['access_token']
                expiration_time = data['expires_in']
                refresh_token = data['refresh_token']

                auth = get_authenticator()
                if auth.login_using_token(request, access_token):
                    response = HttpResponseRedirect(next)
                    cookie_args = {'max_age': expiration_time,
                                   'domain': settings.OAUTH_COOKIE_DOMAIN}
                    response.set_cookie('access_token',
                                        access_token,
                                        **cookie_args)
                    response.set_cookie('expiration_time',
                                        expiration_time,
                                        **cookie_args)
                    response.set_cookie('refresh_token',
                                        refresh_token,
                                        **cookie_args)
                    return response
        else:
            logger.debug('received response %s from auth service. can\'t login' % authresponse)

        return HttpResponseForbidden()


class LogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super(LogoutView, self).dispatch(request, *args, **kwargs)
        domain = settings.OAUTH_COOKIE_DOMAIN

        # clear the SSO cookies to logout from all portal apps
        for c in ['access_token', 'expiration_time', 'refresh_token']:
            response.set_cookie(c, max_age=0, domain=domain)

        return response
