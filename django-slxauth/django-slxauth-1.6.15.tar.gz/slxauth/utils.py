import logging

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group


logger = logging.getLogger(__name__)


def is_authorized(authorities, required):
    """
    :param authorities: list of given roles
    :param required: list of required roles
    :returns: true if any required role exists
    """
    return len(set(required) & set(authorities)) > 0


def get_authenticator():
    return TokenAuthenticator(
        settings.OAUTH_ROLES_REQUIRED,
        settings.OAUTH_ROLES_STAFF,
        settings.OAUTH_ROLES_SUPERUSER,
        settings.OAUTH_PUBLIC_KEY,
        settings.PORTAL_CONFIG_URL
    )


class TokenAuthenticator:
    def __init__(self,
                 required_roles,
                 staff_roles,
                 superuser_roles,
                 oauth_publickey,
                 portal_config_url):
        self.required_roles = required_roles
        self.staff_roles = staff_roles
        self.superuser_roles = superuser_roles
        self.oauth_publickey = oauth_publickey
        self.portal_config_url = portal_config_url


    def _getpk(self, minipk):
        """
        ### mySolarlux convention ###
        since the publickey is stored in a no-newline env-var we need to add a prefix and suffix to it,
        to be able to use it as a jwt publickey signature
        """
        return """-----BEGIN PUBLIC KEY-----
%s
-----END PUBLIC KEY-----""" % minipk

    def decode_token(self, token):
        oauth_public_key = self._getpk(self.oauth_publickey)
        # validate the oauth2 token
        return jwt.decode(token, oauth_public_key, algorithms=['RS256'])

    def check_access(self, authorities):
        # check if superuser
        if is_authorized(authorities, self.superuser_roles):
            return True

        # if not superuser, check if any required role exists
        return len(self.required_roles) == 0 or is_authorized(authorities, self.required_roles)


    def get_unsaved_user_from_token(self, access_token, token_data):

        if not self.check_access(token_data['authorities']):
            return None

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(email=token_data['email'])

        logger.debug('%s user %s' % ('creating' if created else 'updating', user.email))

        user.access_token = access_token
        user.customer_no = token_data['customerNumber']
        user.customer_name = token_data['customerName']
        user.last_name = token_data['lastName']
        user.first_name = token_data['firstName']
        user.title = token_data['title']
        user.is_customer_admin = token_data['isCustomerAdmin']
        user.language = token_data['language']
        user.crm_contact_id = token_data['crmContactId']
        user.um_id = token_data['id']

        user_groups = user.groups.all()

        logger.debug('deleting exited groups for user %s' % user.email)
        for group in user_groups:
            if group.name not in token_data['authorities']:
                group.user_set.remove(user)

        logger.debug('creating joined groups for user %s' % user.email)
        for role in token_data['authorities']:
            if role not in [x.name for x in user_groups]:
                group, created = Group.objects.get_or_create(name=role)
                user.groups.add(group)

        user.is_active = self.check_access(token_data['authorities'])
        user.is_staff = is_authorized(token_data['authorities'], self.staff_roles)
        user.is_superuser = is_authorized(token_data['authorities'], self.superuser_roles)

        logger.debug('finished user extraction from token')
        return user


    def get_unsaved_user_from_token_and_portal_config(self, access_token, token_data, portal_config):

        if not self.check_access(token_data['authorities']):
            return None

        user = self.get_unsaved_user_from_token(access_token, token_data)

        if portal_config and 'fetch-user-info-url' in portal_config:
            logger.debug('fetching user info from portal config for %s' % user.email)
            user_profile_response = None

            try:
                user_profile_response = requests.get(portal_config['fetch-user-info-url'],
                                                     headers={'Authorization': 'Bearer %s' % access_token}, timeout=0.5)
                logger.debug('user profile response: %s' % user_profile_response)
            except Exception as e:
                logger.error('could not fetch user info: %s' % e)

            if user_profile_response and user_profile_response.status_code == 200:
                user_profile = user_profile_response.json()
                user.avatar_attachment_id = user_profile['avatarAttachmentId']
                user.company_logo_attachment_id = user_profile['companyLogoAttachmentId']
                logger.debug('updated user %s from portal config' % user.email)

        return user


    def login_using_token(self, request, access_token):

        logger.debug('extracting user info from access-token %s' % access_token)
        try:
            # validate the oauth2 token
            token_data = self.decode_token(access_token)
        except:
            return False

        if not self.check_access(token_data['authorities']):
            return False

        portal_config_response = None

        logger.debug('beginning user login from token')
        try:
            # load more infos...
            portal_config_response = requests.get(self.portal_config_url, headers={
                'Authorization': 'Bearer %s' % access_token
            }, timeout=0.5)
            logger.debug('portal config response: %s' % portal_config_response)
        except Exception as e:
            logger.error('could not load remote portal config: %s' % e)

        user = None

        if portal_config_response and portal_config_response.status_code == 200:
            try:
                logger.debug('getting user from access token and portal config')
                portal_config = portal_config_response.json()
                user = self.get_unsaved_user_from_token_and_portal_config(access_token, token_data, portal_config)
            except Exception as e:
                logger.error('could not get user from access token and portal config: %s' % e)

        if not user:
            logger.debug('getting user from access token without portal config')
            user = self.get_unsaved_user_from_token(access_token, token_data)

        logger.debug('saving user object')
        user.save()
        logger.debug('logging in user %s' % user.email)
        login(request, user)
        return True
