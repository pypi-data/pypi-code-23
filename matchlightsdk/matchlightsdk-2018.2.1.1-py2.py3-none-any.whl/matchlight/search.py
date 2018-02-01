"""An interface for searching the Matchlight fingerprints database."""
from __future__ import absolute_import

import datetime
import json

import matchlight.error
import pylibfp


class SearchMethods(object):
    """Provides methods for interfacing with the search API."""

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes a search interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def search(self, query=None, email=None, ssn=None, phone=None,
               fingerprints=None):
        """Performs a Matchlight search.

        Provides a retrospective search capability. User can only
        perform one search type at time. Search type is specified using
        keyword arguments.

        Example:

            Search for text::

                >>> ml.search(query="magic madness heaven sin")

            Search for an email address::

                >>> ml.search(email="familybird@terbiumlabs.com")

            Search for a social security number::

                >>> ml.search(ssn="000-00-0000")

            Search for a phone number::

                >>> ml.search(phone="804-222-1111")

        Args:
            query (:obj:`str`, optional): A text query.
            email (:obj:`str`, optional): A valid email address.
            ssn (:obj:`str`, optional): A social security number.
            phone (:obj:`str`, optional): A phone number.
            fingerprints (:obj:`list` of :obj:`str`, optional): A
                sequence of Matchlight fingerprints.


        Returns:
            :obj:`list` of :obj:`dict`: Each search result returns a
                score, url, ts.

        """
        # only search for one thing at a time.
        if sum([1 for k in [query, fingerprints, email, ssn, phone]
                if k is not None]) != 1:
            raise matchlight.error.SDKError(
                'Input Error: Must specify exactly one search type per call.')

        if email:
            fingerprints = pylibfp.fingerprints_pii_email_address(str(email))
        elif phone:
            fingerprints = pylibfp.fingerprints_pii_phone_number(str(phone))
        elif ssn:
            fingerprints = pylibfp.fingerprints_pii_ssn(str(ssn))
        elif query:
            result_json = pylibfp.fingerprint(
                query, flags=pylibfp.OPTIONS_TILED)
            result = json.loads(result_json)
            fingerprints = result['data']['fingerprints']

        if any(isinstance(element, list) for element in fingerprints):
            raise matchlight.error.SDKError(
                'Fingerprinter Failed: List of Lists')

        data = {'fingerprints': list(fingerprints)}
        response = self.conn.request(
            '/detailed_search',
            data=json.dumps(data),
            endpoint=self.conn.search_endpoint,
        )
        try:
            results = response.json()['results']
        except KeyError:
            raise matchlight.error.SDKError('Failed to get search results')
        for result in results:
            for url in result['urls']:
                yield {
                    'score': result['score'],
                    'ts': datetime.datetime.fromtimestamp(url[0]),
                    'url': url[1]
                }
