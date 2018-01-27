from comala.workflows.models.workflow import PageWorkflow
import logging
import requests
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ComalaWorkflowsClient:
    """
    This is the main interface into this API from external applications. It
    provides an abstraction over the REST API which comala workflows provides
    in Confluence.
    """
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
        self._base_api_url = '{}/rest/cw/1'.format(self._url)
        self._client = None  # type: requests.Session

    def __enter__(self):
        self._client = requests.session()
        self._client.auth = self._basic_auth

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    def status(self, page_id, expand=None):
        # type: (int, Optional[List[str]]) -> PageWorkflow
        """
        Get the status of a page as understood by Comala Workflows.

        c.f. http://bit.ly/2mGKv26 for the official docs.

        :param page_id: The confluence page ID.
        :param expand: An optional comma separated string of properties to
        expand. Valid values are: state, states, approvals, actions, tasks.

        :return: A PageWorkflow object containing information about the page.
        """
        url = '{}/content/{}/status'.format(self._base_api_url, page_id)
        params = {}

        if expand:
            params['expand'] = expand

        if self._client:
            result = self._client.get(url, params=params).json()
        else:
            result = requests.get(url, params=params, auth=self._basic_auth).json()

        return PageWorkflow(result)
