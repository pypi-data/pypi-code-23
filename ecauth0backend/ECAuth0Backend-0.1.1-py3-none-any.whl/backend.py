import json

import requests
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from ECAuth0Backend.models import A0User
from ECAuth0Backend.settings import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, \
    AUTH0_CALLBACK_URL


def get_or_create_user(user_id, email, email_verified, name):
    """
    Get or create a user.
    :user_id: the Auth0 user_id
    :email: the user's email
    :email_verified: whether or not the user's email is verified
    :name: the user's name
    :return:
    """
    try:
        user = A0User.objects.get(uid=user_id)
        user.email = email
        user.email_verified = email_verified
        user.name = name
        user.save()
    except User.DoesNotExist:
        user = A0User.objects.create(
            uid=user_id,
            email=email,
            email_verified=email_verified,
            name=name
        )
    return user


class Auth0Backend(object):
    def get_user(self, user_id):
        try:
            user = A0User.objects.get(uid=user_id)
        except User.DoesNotExist:
            return None
        return user

    def authenticate(self, **credentials):
        authorization_code = credentials.get('code')
        if not authorization_code:
            return None
        else:
            authorization_code = authorization_code[0]
        json_header = {'content-type': 'application/json'}
        token_url = "https://{domain}/oauth/token".format(
            domain=AUTH0_DOMAIN
        )
        token_payload = {
            'client_id': AUTH0_CLIENT_ID,
            'client_secret': AUTH0_CLIENT_SECRET,
            'redirect_uri': AUTH0_CALLBACK_URL,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        token_info = requests.post(token_url, data=json.dumps(token_payload), headers=json_header).json()
        try:
            user_url = "https://{domain}/userinfo?access_token={access_token}".format(
                domain=AUTH0_DOMAIN,
                access_token=token_info['access_token']
            )
        except KeyError:
            raise HttpResponseBadRequest

        user_info = requests.get(user_url).json()

        return get_or_create_user(
            user_id=user_info.get('user_id'),
            email=user_info.get('email'),
            email_verified=user_info.get('email_verified', False),
            name=user_info.get('name')
        )



