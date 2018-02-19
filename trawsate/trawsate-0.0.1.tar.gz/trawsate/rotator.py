# -*- coding: utf-8 -*-
from typing import Any, Iterable, Dict
from trawsate import travis, single, parallel

AccessKeyPair = Any


class Rotator:
    """
    Rotates keys.
    """

    def __init__(self, travis_token: str):
        """
        Initialise a new rotator.

        :param travis_token: A valid Travis API token.
        """
        self._session = travis.create_session(travis_token)

    def key(self, username: str, slug: str) -> AccessKeyPair:
        """
        Rotate a single key.

        :param username: The username of the owner of the key.
        :param slug: The slug of the GitHub repository responsible for the
                     user.
        :return: The created key pair.
        """
        return single.rotate_key(username, slug, self._session)

    def keys(self, usernames_slugs: Dict[str, str], parallelism: int) \
            -> Iterable[parallel.JobResult]:
        """
        Rotate one or more keys.

        :param usernames_slugs: A map from username to responsible repo slug.
        :param parallelism: The maximum number of users to rotate in parallel.
        :return: The result of each rotation, in the same order users were
                 provided.
        """
        yield from parallel.rotate_keys(usernames_slugs, self._session,
                                        parallelism)
