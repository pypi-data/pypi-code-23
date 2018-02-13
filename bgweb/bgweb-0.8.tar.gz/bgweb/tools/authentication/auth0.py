"""
Auth0 (https://auth0.com/) enables authentication
of users using different system.

Currently only social login and traditional DB
with user-password are used.

The Authentication system is traditional web application
is as follows:
- A lock object (JavaScript) makes a request to the Auth0 server.
- The servers responds to an URL specified in the lock object with
   a code that identifies the user
- The Authentication tool must use this code to authenticate the
  user in the Auth0 servers, which respond with the user information

As of December 2016, the users were logged in right after
signing in. Moreover, email verification was not required
as email were send using the Auth0 service which should not
be used for development.
"""


import http.client
import json
import logging
import ssl
import urllib

import cherrypy
from oauthlib.common import to_unicode
from oauthlib.oauth2 import AccessDeniedError
from requests_oauthlib import OAuth2Session

from bgweb.profile.auth0_profile import Auth0Profile
from .authentication import AuthenticationTool, AuthError, ITokenAuthentication, TokenNotFoundError, UserNotFoundError


class Auth0Error(AuthError):

    def __init__(self, message, status=None, reason=None):
        self.message = message
        self.status = status
        self.reason = reason


class Auth0(AuthenticationTool):

    def __init__(self, configuration, app_url, login_path, logout_path, force_login_function, user_id_str='user_id', add_profile=True, login_redirect=None, logout_redirect=None):
        """
        This tool is intended to intercept all requests to the server and check if the request
        is done to one of the login or logout paths or to a page/resource that is protected.

        Args:
            configuration (dict): must contain the client secret, key and domain
            app_url (str): base URL for the application
            login_path (str): path to be intercepted for the log in
            logout_path (str): path to be intercepted for the log in
            force_login_function (func): function to be called if the login is required
            user_id_str (str): string that is used in the session as key of the value corresponding to the user ID
            login_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).
               The application should store in the session the redirect URL in "auth_redirect_url"
            logout_redirect (str): URL to redirect after the user logs out via HTTPRedirect (default to None).

        In order to emulate the reload of the page after log in done with Mozilla persona,
        the tool expects to receive the URL to redirect from the state parameter of the lock object.
        In this implementation it is done using the window.location.href

        Limitations are:
        - authentication_user_information is used in the cherrypy session to
            store additional information from the user
        - If you want the page reload after log in feature to work, the force login
          function should retrieve the code for the page without changing the URL.
          E.g.: give a function that does something like:
          return self.env.get_template('login.html').render
        """
        self.conf = configuration

        self.__base_url = app_url

        mount_point = urllib.parse.urlparse(app_url).path
        # Add missing parameters to auth0
        mount_point = '' if mount_point in ['', '/'] else mount_point
        mount_point = mount_point[1:] if mount_point.startswith('/') else mount_point
        mount_point = mount_point[:-1] if mount_point.endswith('/') else mount_point

        auth0_login_url = urllib.parse.urljoin(app_url, mount_point + login_path)
        auth0_logout_url = urllib.parse.urljoin(app_url, mount_point + logout_path)

        self.__login_path = login_path
        self.__logout_path = logout_path
        super(Auth0, self).__init__(self.authenticate, force_login_function, user_id_str)

        auth0_base_url = 'https://{}'.format(self.conf['AUTH0_DOMAIN'])
        scope = to_unicode('openid profile')
        self.__oauth = OAuth2Session(self.conf['AUTH0_CLIENT_ID'], redirect_uri=auth0_login_url, scope=scope)
        self.__authorization_url = urllib.parse.urljoin(auth0_base_url, 'authorize')

        self.__access_token_url = urllib.parse.urljoin(auth0_base_url, '/oauth/token')
        self.__audience = urllib.parse.urljoin(auth0_base_url, '/userinfo')

        params = {'returnTo': auth0_logout_url, 'client_id': self.conf['AUTH0_CLIENT_ID']}
        self.__logout_url = auth0_base_url + '/v2/logout?' + urllib.parse.urlencode(params)

        logging.getLogger(__name__).debug('Using Auth0. Capturing %s for signin and %s for singout' % (login_path, logout_path))

        self.__login_redirect = login_redirect
        self.__logout_redirect = logout_redirect
        self.__use_profile = add_profile

    def authenticate(self, require=None):
        """
        Entry point for this tool.
        Intercepts the URL matching login_path or logout_path and changes the handlers.
        Additionally, checks if the request resource is under *authentication.require*

        Args:
            login_path (str): path to be intercepted when logging in
            logout_path (str): path to be intercepted when logging out
            require (str): this parameter is given for the static content with the
               authentication.require

        """
        if cherrypy.request.path_info == self.__login_path:
            cherrypy.request.handler = self.authentication_callback
            return
        elif cherrypy.request.path_info == self.__logout_path:
            cherrypy.request.handler = self.logout
            return

        if require is not None and self.get_user() is None:
            raise cherrypy.HTTPRedirect(require.format(cherrypy.request.path_info))

        conditions = cherrypy.request.config.get('authentication.require', None)

        if conditions is not None:

            if self.get_user() is None:
                # the user is not logged in, but the tool is enabled, so instead
                #  of allowing the default handler to run, respond instead with
                #  the authentication page.
                cherrypy.request.handler = self.force_login
            else:

                for condition in conditions:
                    # A condition is just a callable that returns true or false
                    if not condition(self.get_user()):
                        cherrypy.request.handler = self.force_login

    def authentication_callback(self):
        """
        Handler for log-ins.

        Raises
            HTTPError if authentication fails

        The redirect URL is expected from the state parameter of the Auth0 Lock.

        """
        code = cherrypy.request.params.get('code', None)
        state = cherrypy.request.params.get('state', None)

        session_state = cherrypy.session.get('auth_state', None)
        if session_state is not None and state != session_state:
            raise cherrypy.HTTPError(500, "Invalid. Error when connecting with Auth0. Incorrect state")

        error = cherrypy.request.params.get('error', None)
        error_description = cherrypy.request.params.get('error_description', None)

        if error is not None:
            raise cherrypy.HTTPError(500, "Invalid. Error when connecting with Auth0. {} : {}".format(error, error_description))

        token = self.__oauth.fetch_token(
            self.__access_token_url,
            code=code,
            method='POST',
            client_secret=self.conf['AUTH0_CLIENT_SECRET'])

        headers = {'authorization': 'Bearer ' + token['access_token']}
        try:
            resp = self.__oauth.get(self.__audience, headers=headers)
        except AccessDeniedError:
            raise cherrypy.HTTPError(500, "Invalid. Error when connecting with Auth0")

        user_info = resp.json()

        # We're saving all user information into the session
        email = user_info.get('email', None)
        if email is None:
            raise cherrypy.HTTPError(500, "Error when connecting with Auth0. Email missing.")
        self.login_user(email)

        logging.getLogger(__name__).info('User %s has logged in' % email)

        if self.__use_profile:
            user_info['token_id'] = token['id_token']
            user = self.get_user()
            user.profile = Auth0Profile(user.id, user_info, self.conf['AUTH0_DOMAIN'])  # Add profile to the user

        if self.__login_redirect is not None:
            raise cherrypy.HTTPRedirect(self.__login_redirect)
        else:
            redirect_url = cherrypy.session.pop('auth_redirect_url', self.__base_url)
            raise cherrypy.HTTPRedirect(redirect_url)

    def logout(self):
        """
        Handler for log-outs.

        """
        cherrypy.response.headers['Cache-Control'] = 'no-cache'

        self.logout_user()

        if self.__logout_redirect is not None:
            raise cherrypy.HTTPRedirect(self.__logout_redirect)
        else:
            redirect_url = cherrypy.session.pop('auth_redirect_url', self.__base_url)
            raise cherrypy.HTTPRedirect(redirect_url)

    def get_login_url(self):
        login_url, state = self.__oauth.authorization_url(self.__authorization_url)
        cherrypy.session['auth_state'] = state
        return login_url

    def get_logout_url(self):
        return self.__logout_url


class Auth0Token(ITokenAuthentication):

    def __init__(self, domain, client, secret):

        self.domain = domain
        self.client = client
        self.secret = secret

        self.__connect()

        self.retried = False  # flag to avoid possible infinite loops

    def __connect(self):
        conn = http.client.HTTPSConnection(self.domain, context=ssl._create_unverified_context())

        payload = {'client_id': self.client,'client_secret': self.secret, 'audience': 'https://'+self.domain+'/api/v2/','grant_type':'client_credentials'}
        payload = json.dumps(payload)

        headers = {'content-type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()

        data = res.read()

        data = data.decode("utf-8")

        conn.close()

        if res.status < 400:
            data = json.loads(data)
            self.token = data['access_token']
            self.token_type = data['token_type']
        else:
            raise Auth0Error(data, res.status, res.reason)

    def check_token(self, user_id, token, application=None):

        conn = http.client.HTTPSConnection(self.domain, context=ssl._create_unverified_context())

        headers = {'authorization': ' '.join([self.token_type, self.token])}

        parameter = urllib.parse.quote('email:"{}"'.format(user_id))
        conn.request("GET", "/api/v2/users?q={}".format(parameter), headers=headers)

        res = conn.getresponse()
        data = res.read()

        data = data.decode("utf-8")

        conn.close()

        # print('----->', res.status, res.msg)

        if res.status < 400:
            self.retried = False
            data = json.loads(data)
            # One use can have multiple identities, one for each identity provider
            metadata_list = []
            for user_data in data:
                user_email = user_data.get('email', None)
                if user_email == user_id:
                    metadata_list.append(user_data.get('user_metadata', None))
            if not metadata_list:
                logging.getLogger(__name__).warning('Cannot find user %s' % user_id)
                raise UserNotFoundError()
            user_tokens = set()
            accepted_apps = set()
            for metadata in metadata_list:
                if metadata is None:
                    continue
                token = metadata.get('api_token', None)
                if token is not None:
                    user_tokens.add(token)
                accepted_apps.update(set(metadata.get('terms', [])))
            if not user_tokens:
                logging.getLogger(__name__).warning('Cannot find token for %s' % user_id)
                raise TokenNotFoundError()
            if application not in accepted_apps:
                logging.getLogger(__name__).info('User %s has not accepted the terms' % user_id)
                raise AuthError('Terms not accepted for this app. Please register and accept the terms in the application site')
            return token in user_tokens
        else:
            # It is possible to get an error here if the token expires (last for 1 day)
            # When that happens, we try to connect again to Auth0 to ask for a new token and do the check again
            if self.retried:
                logging.getLogger(__name__).error('Error retrying Auth0 connection for tokens')
                raise Auth0Error(data, res.status, res.reason)
            else:
                self.retried = True
                self.__connect()
                return self.check_token(user_id, token)
