# -*- coding: utf-8 -*-

"""
yellowant.endpoints
~~~~~~~~~~~~~~~~~~~~~
"""

import os
import warnings
from io import BytesIO
from time import sleep

from .advisory import YellowAntDeprecationWarning


class Endpoints(object):

    def get_user_profile(self, **params):
        """Returns the profile for the authenticating user.

        """
        return self.get('user/profile/', params=params)

    def create_user_integration(self, **params):  # pragma: no cover
        """Creates a new user integration for the authenticating application

        """
        return self.post('user/integration/', params=params)

    def delete_user_integration(self, **params):  # pragma: no cover
        """Delete a new user integration for the authenticating application

        """
        return self.delete('user/integration/%s/' % params.get('id'), params=params)


    def get_user_integration(self, **params):  # pragma: no cover
        """Delete a new user integration for the authenticating application

        """
        return self.get('user/integration/%s/' % params.get('id'), params=params)

    def update_user_integration(self, **params):  # pragma: no cover
        """"Updates a new user integration for the authenticating application

        """
        return self.patch('user/integration/%s/' % params.get('id'), params=params)


    def add_message(self, **params):  # pragma: no cover
        """Sends a message to the authenticated user

        """
        return self.post('user/message/', params=params)

    def create_webhook_message(self, **params):  # pragma: no cover
        """Sends a message to the authenticated user

        """
        return self.post('user/application/webhook/%s/'% (params.get('webhook_id') or params.get('webhook_name')), params=params)


    def get_application_messages(self, **params):
        """Returns a list of user messages for the user_integration_id

        """
        return self.patch('user/applications/%s/messages/' % params.get('user_integration_id'), params=params)


    def get_application_message(self, **params):
        """Returns a single message, specified by the user_integration_id and message_id parameters

        """
        return self.patch('user/applications/%s/messages/%s/' % (params.get('user_integration_id'), params.get('message_id')), params=params)


    def get_application_logs(self, **params):
        """Returns a list of logs by the application for the current user

        """
        return self.get('user/logs/', params=params)

    # OAuth
    def revoke_token(self, **params):  # pragma: no cover
        """Allows a registered application to revoke an issued OAuth 2 Bearer
        Token by presenting its client credentials.

        """
        return self.post('oauth2/revoke_token/', params=params)


    def get_supported_languages(self, **params):
        """Returns the list of languages supported by YellowAnt along with
        their ISO 639-1 code.

        """
        return self.get('help/languages/', params=params)


    def create_application(self, **params):
        """Creates an application.

        """
        return self.post('developers/create/', params=params)

    def update_application(self, **params):
        """Updates an application

        """
        return self.patch('developers/create/', params=params)

    def get_privacy_policy(self, **params):
        """Returns YellowAnt's Privacy Policy

        """
        return self.get('help/privacy/', params=params)

    def get_tos(self, **params):
        """Return the YellowAnt Terms of Service

        """
        return self.get('help/tos/', params=params)

    def get_application_rate_limit_status(self, **params):
        """Returns the current rate limits for methods belonging to the
        specified resource families.

        """
        return self.get('application/rate_limit_status/', params=params)


YELLOWANT_HTTP_STATUS_CODE = {
    200: ('OK', 'Success!'),
    204: ('OK', 'Modified!'),
    304: ('Not Modified', 'There was no new data to return.'),
    400: ('Bad Request', 'The request was invalid. An accompanying \
          error message will explain why. This is the status code \
          will be returned during rate limiting.'),
    401: ('Unauthorized', 'Authentication credentials were missing \
          or incorrect.'),
    403: ('Forbidden', 'The request is understood, but it has been \
          refused. An accompanying error message will explain why. \
          This code is used when requests are being denied due to \
          update limits.'),
    404: ('Not Found', 'The URI requested is invalid or the resource \
          requested, such as a user, does not exists.'),
    405: ('Method not allowed', 'The URI requested is invalid or the resource \
          requested, such as a user, does not exists.'),
    406: ('Not Acceptable', 'Returned by the Search API when an \
          invalid format is specified in the request.'),
    410: ('Gone', 'This resource is gone. Used to indicate that an \
          API endpoint has been turned off.'),
    422: ('Unprocessable Entity', 'Returned when an image uploaded to \
          POST account/update_profile_banner is unable to be processed.'),
    429: ('Too Many Requests', 'Returned in API v1.1 when a request cannot \
          be served due to the application\'s rate limit having been \
          exhausted for the resource.'),
    500: ('Internal Server Error', 'Something is broken. Please post to the \
          group so the YellowAnt team can investigate.'),
    501: ('Not Implemented', 'User is not subscribed to this webhook data'),
    502: ('Bad Gateway', 'YellowAnt is down or being upgraded.'),
    503: ('Service Unavailable', 'The YellowAnt servers are up, but overloaded \
          with requests. Try again later.'),
    504: ('Gateway Timeout', 'The YellowAnt servers are up, but the request \
          couldn\'t be serviced due to some failure within our stack. Try \
          again later.'),
}
