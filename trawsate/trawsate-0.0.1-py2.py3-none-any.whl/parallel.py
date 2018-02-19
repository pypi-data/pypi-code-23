# -*- coding: utf-8 -*-
from typing import Any, Dict, Iterable, Tuple
from concurrent.futures import ThreadPoolExecutor
import requests
import boto3

from trawsate import single
from trawsate.promise import Promise

AccessKeyPair = Any

iam = boto3.resource('iam')


class JobResult:
    """
    Represents the result of attempting to change the active access key for a
    user.
    """

    def __init__(self, username: str, slug: str,
                 outcome: Promise[AccessKeyPair]):
        """
        Initialise a new result.

        :param username: The username whose access key we attempted to rotate.
        :param slug: The slug of the GitHub repository associated with the user
                     through Travis.
        :param outcome: The nested result of the operation.
        """
        self.username = username
        self.slug = slug
        self.result = outcome

    def __str__(self) -> str:
        return f'{self.username} ({self.slug}): {self.result}'


def _execute_job(inputs: Tuple[str, str, requests.Session]) \
        -> Promise[AccessKeyPair]:
    """
    Rotate the active access key for a user. This method will not throw any
    exceptions.

    :param inputs: A triple containing the username of the user, the repo slug,
                   and a session to use for interaction with Travis's API.
    :return: A promise representing success or failure.
    """
    from trawsate import AccessKeyStateError, TravisError
    username, slug, session = inputs
    try:
        return Promise.fulfilled(single.rotate_key(username, slug, session))
    except (iam.meta.client.exceptions.NoSuchEntityException,
            AccessKeyStateError, TravisError) as e:
        return Promise.rejected(e)


def rotate_keys(usernames_slugs: Dict[str, str], session: requests.Session,
                parallelism: int = 20) -> Iterable[JobResult]:
    """
    Rotate the active access key for many users.

    :param usernames_slugs: A map from AWS username to associated repository
                            slug.
    :param session: A session to use for interaction with Travis.
    :param parallelism: The maximum number of users to update in parallel.
    :return: The result of each rotation. If an ordered dict is passed in, this
             is guaranteed to have the same order.
    """
    inputs = [(username, slug, session)
              for username, slug in usernames_slugs.items()]
    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        for (username, slug, _), result in \
                zip(inputs, executor.map(_execute_job, inputs)):
            yield JobResult(username, slug, result)
