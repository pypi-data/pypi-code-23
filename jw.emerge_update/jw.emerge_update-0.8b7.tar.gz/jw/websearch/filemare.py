"""
FileMare search
"""

from .base import Base

class Search(Base):
    """
    FileMare Search
    """

    _baseUrl = 'http://filemare.com'
    _searchPath = '/search/{query}'
    _linkArgs = ('div',)
    _linkAttr = {'class_': 'descr'}
    _zoom = (
        ('__getattr__', ('a',)),            # get <a> of <div class="descr">
        ('__getitem__', ('href',)),         # get href= of <a>
        ('replace', ('/browse/', 'http://filemare.com/browse/'))   # replace URL
    )

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
        # TODO: handle next page
        return None
