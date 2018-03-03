"""
DuckDuckGo search
"""

from .base import Base

class Search(Base):
    """
    DuckDuckGo Search
    """

    _baseUrl = 'https://duckduckgo.com'
    _searchPath = '/html?q={query}'
    _linkAttr = {'class_': 'result__a'}

    def __init__(self):
        """
        Create a Search object
        """

    def nextPage(self, dom):
        """
        Next page

        :param dom: DOM of page to get next page of
        :type dom: BeautifulSoup
        :return: URL
        :rtype:
        """
        return None
