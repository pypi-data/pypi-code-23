from communardo.metadata.models.metadatavalue import MetadataValue
from communardo.metadata.models.pagemetadata import PageMetadata
from enum import Enum
import logging
import requests
from typing import Iterable, Optional, Tuple


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SearchSortDirection(Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class MetadataClient:
    """
    This is the main interface into this API from external applications. It
    provides an abstraction over the REST API which communardo metadata
    provides in Confluence.
    """
    default_page_size = 10

    def __init__(self, url, basic_auth):
        # type: (str, Tuple[str, str]) -> None
        """
        :param url: The base URL on which you access the confluence instance
        in a web browser.
        :param basic_auth: A tuple of username/password which can access the
        Confluence instance.
        """
        self._url = url
        self._basic_auth = basic_auth
        self._base_api_url = '{}/rest/communardo/metadata/latest/filter'.format(self._url)
        self._client = None  # type: requests.Session

    def __enter__(self):
        self._client = requests.session()
        self._client.auth = self._basic_auth

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    def search(self, query=None, cql=None, sort='content-name-untokenized',
               sort_direction=SearchSortDirection.ASCENDING, fields=None):
        # type: (Optional[str], Optional[str], str, SearchSortDirection, Optional[str]) -> Iterable[PageMetadata]
        """
        The Communardo Metadata plugin exposes a single REST API entry point
        which acts as a way to filter all documents on the confluence instance
        and return their metadata.

        The REST API is paged but that is abstracted away by this library so
        you can query all data by simply iterating over the result of this
        query.

        :param query: Either query or CQL must be set. Query refers to a
        lucene query.
        :param cql: Either query or CQL must be set. CQL refers to the advanced
        CQL search function in confluence.
        :param sort: The name of the field to sort on. Defaults to title.
        :param sort_direction: The direction to sort is either ASCENDING or
        DESCENDING with the default being ASCENDING.
        :param fields:
        :return:
        """
        params = {
            'sort': sort,
            'sortdirection': sort_direction.value,
            'pagesize': MetadataClient.default_page_size
        }

        if (not query and not cql) or (query and cql):
            raise ValueError('Either the query or cql parameter must be set but not both')
        elif query:
            params['query'] = query
        else:
            params['cql'] = cql

        if fields:
            params['fields'] = fields

        page_number = 1
        last_page = False
        while not last_page:
            url = '{}/{}'.format(self._base_api_url, page_number)

            if self._client:
                results = self._client.get(url, params=params).json()
            else:
                results = requests.get(url, params=params, auth=self._basic_auth).json()

            if 'searchResults' in results:
                for result in results['searchResults']:
                    yield PageMetadata(result['pageId'], result['pageTitle'], result['pageUrl'], result['contentType'],
                                       [MetadataValue(v['id'], v['key'], v['title'], v['content'])
                                        for v in result['values']])

            # Check if we should stop iterating
            if 'pager' not in results or results['pager']['currentPage'] == results['pager']['pageCount']:
                last_page = True

    def __str__(self):
        return self._base_api_url
