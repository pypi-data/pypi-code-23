# -*- coding: utf-8 -*-
from typing import Any, Optional
import logging
import boto3
import requests

from trawsate import travis

IamUser = Any
AccessKeyPair = Any

logger = logging.getLogger(__name__)

iam = boto3.resource('iam')


class AccessKeyStateError(Exception):
    """
    Raised when a user's access keys are in a state we cannot handle and/or
    require that they are not in.
    """
    pass


def _handle_existing_keys(user: IamUser) -> Optional[IamUser]:
    """
    Get a user's keys in a state where we can safely create a new key.

    :param user: The user whose keys to scan.
    :return: The user to deactivate after creating a new key, if any.
    """
    # without conversion to list, we can't call len()
    access_keys = list(user.access_keys.all())
    access_key_count = len(access_keys)

    for access_key in access_keys:
        logger.debug('Found key %s', access_key.id)

    if access_key_count == 0:
        # nothing to do
        return None

    if access_key_count == 1:
        access_key = access_keys[0]

        if access_key.status == 'Active':
            logger.debug('Key %s is active', access_key.id)
            return access_key

        return None

    if access_key_count == 2:
        key_a, key_b = access_keys

        if key_a.status == 'Active' and key_b.status == 'Active':
            raise AccessKeyStateError(f'There are currently two active access '
                                      f'keys ({key_a.id}, {key_b.id}); not '
                                      f'sure what to do')

        if key_a.status == 'Inactive' and key_b.status == 'Inactive':
            # delete oldest key
            key_a.delete()
            return None

        # one active, one inactive
        if key_a.status == 'Active':
            key_b.delete()
            return key_a

        key_a.delete()
        return key_b

    raise AccessKeyStateError(f'Unexpected number of access keys: '
                              f'{access_key_count}')


def rotate_key(username: str, slug: str,
               travis_session: requests.Session) -> AccessKeyPair:
    """
    Generate and set a new key in Travis for an AWS user.

    :param username: The username of the AWS user whose access key to rotate.
    :param slug: The "<username>/<repo_name>" of the GitHub repo to update in
                 Travis.
    :param travis_session: The session to use to interact with Travis's API.
    :raises NoSuchEntityException: If no user with `username` exists.
    :raises AccessKeyStateError: If the user's access keys are in an invalid
                                 state.
    :raises travis.TravisError: If an error occurs updating Travis environment
                                variables.
    :return: The new access key pair.
    """
    logger.debug('Rotating access key for user %s', username)
    user = iam.User(username)
    logger.debug('User ARN: %s', user.arn)
    to_deactivate = _handle_existing_keys(user)
    if to_deactivate is not None:
        logger.debug('Will deactivate %s after rotation', to_deactivate.id)
    logger.debug('Creating new access key')
    access_key = user.create_access_key_pair()
    logger.debug('Created access key %s', access_key.id)
    travis.update_access_key(slug, access_key, travis_session)
    if to_deactivate is not None:
        logger.debug('Deactivating key %s', to_deactivate.id)
        to_deactivate.deactivate()
    return access_key
