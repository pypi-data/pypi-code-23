from ..utils import user_details_from_token, OAuthException
from ..groupmanager import user_belongs_to_group
from ..models import GroupManagerConnection
from .base import BaseBackend
from django.core.exceptions import PermissionDenied
import logging

# Maps django User attributes to OIDC userinfo keys

logging.basicConfig()
logger = logging.getLogger(__name__)


MISSING_GROUP_MANAGER_SETUP = 'Group Manager not setup.'
USER_NOT_IN_GROUP_FMT = 'User not in required group {}.'

class OAuth2Backend(BaseBackend):

    def get_user_details_map(self):
        """
        Map of django user model keys to the OIDC OAuth keys
        :return:
        """
        return {
            'username': 'sub',
            'first_name': 'given_name',
            'last_name': 'family_name',
            'email': 'email',
        }

    def authenticate(self, service=None, token_dict=None):
        try:
            details = user_details_from_token(service, token_dict)
        except OAuthException as e:
            logger.error('Exception getting user details', e)
            return None
        self.check_user_details(details)
        user = self.save_user(details)
        self.handle_new_user(user, details)
        return user

    def handle_new_user(self, user, details):
        """
        Stub method to allow custom behavior for new OAuth users
        :param user: A django user, created after receiving OAuth details
        :param details: A dictionary of OAuth user info
        :return: None
        """
        pass

    def check_user_details(self, details):
        """
        Stub method to allow checking OAuth user details and raising PermissionDenied if not valid
        :param details: A dictionary of OAuth user info
        """
        pass

    def verify_user_belongs_to_group(self, duke_unique_id, group_name):
        """
        Using the singleton GroupManagerConnection object check to see if a user belongs to a group and raises
        PermissionDenied if missing setup or user is not a member of the group.
        :param duke_unique_id: str: unique duke id for a user
        :param group_name: str: name of the group to check
        """
        group_manager_connection = GroupManagerConnection.objects.first()
        if not group_manager_connection:
            logger.error(MISSING_GROUP_MANAGER_SETUP)
            raise PermissionDenied(MISSING_GROUP_MANAGER_SETUP)
        if not user_belongs_to_group(group_manager_connection, duke_unique_id, group_name):
            raise PermissionDenied(USER_NOT_IN_GROUP_FMT.format(group_name))
