"""
Manager for authorization access of the jobs
"""

import logging

from bgweb.manager.constants import METADATA_USER_ID_STR, METADATA_PUBLIC_ID_STR, METADATA_EXAMPLE_ID_STR, \
    METADATA_SHARED_WITH_STR

from bgweb.manager.utils import BGManagerError
from bgweb.user import BGUser


class AuthorizationError(BGManagerError):
    """
    Manager exception when trying ot access a job without
    the right permissions
    """

    def __init__(self, required_level):
        self.level = required_level
        self.message = 'Authorization error'


none_user = BGUser(None)


class BGAuthorizationManager:
    """
    Handles the right to access a job depending on the requested permissions

    Args:
        configuration:
    """

    def __init__(self, configuration):
        self.admins = [u.lower() for u in configuration.get('admin_users', [])]

    def check_permissions(self, requester, job_metadata, level):
        """
        Check whether a user has access to certain job

        Args:
            requester: user making the query
            job_metadata (dict): job metadata information
            level (str): level requested

        Raises:
            AuthorizationError: when the access rights do not match

        """
        if requester is None:  # unlogged user in application that do not allow anonymous jobs
            requester = none_user

        # Admins have global access
        if requester.id in self.admins:
            return
        elif level == 'a':
            logging.getLogger(__name__).warning('User %s trying to use admin permissions for job %s' % (requester.id, job_metadata.get('id', None)))
            raise AuthorizationError(level)
        # only job owners have write permissions
        elif level == 'w':
            owner = job_metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
            if owner in requester.get_ids():
                return
            else:
                logging.getLogger(__name__).info('User %s trying to use write permissions on job %s' % (requester.id, job_metadata.get('id', None)))
                raise AuthorizationError('w')
        # reading permissions are given to anyone in the share list, as well as for anyone if the job is public or an example
        elif level == 'r':
            if job_metadata.get(METADATA_EXAMPLE_ID_STR, False) or job_metadata.get(METADATA_PUBLIC_ID_STR, False):  # examples and public jobs can be read by anyone
                return
            owner = job_metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
            if owner in requester.get_ids():
                return
            shared = job_metadata.get(METADATA_SHARED_WITH_STR, [])
            for user_id in requester.get_ids():
                if user_id in shared:
                    return

        logging.getLogger(__name__).info('User %s does not have %s permission for job %s' % (level, requester.id, job_metadata.get('id', None)))
        raise AuthorizationError(level)

    @staticmethod
    def is_owner(requester, job_metadata):
        """
        Check if the requester is the job owner

        Args:
            requester: user making the query
            job_id (str): job identifier

        Returns:
            bool:

        """
        if requester is None:
            return False
        owner = job_metadata.get(METADATA_USER_ID_STR, 'anonymous_unknown_user')
        return owner in requester.get_ids()
