"""Base API functionality"""

from urllib.parse import urljoin


class BaseApi:
    """Base class for APIs"""
    def __init__(self, session, base_url, version):
        self.session = session
        self.base_url = base_url
        self.version = version

    def get_url(self, url):
        """
        Create a absolute url to the endpoint

        Args:
            url(str): the relative url

        Returns:
            str: the absolute url
        """
        return urljoin(
            self.base_url,
            "/api/{}/{}".format(self.version, url.lstrip("/"))
        )
