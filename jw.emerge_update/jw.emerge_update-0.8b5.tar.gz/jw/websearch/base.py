"""
Base search class
"""
import requests
from __future__ import print_function

from bs4 import BeautifulSoup

class Base(object):
    """
    Base class
    """

    _zoom = ()
    _linkArgs = ('a',)

    def search(self, query):
        """
        Search for query
        """
        pageUrl = self._baseUrl + self._searchPath.format(query=query)
        print('pageUrl:', pageUrl)
        dom = BeautifulSoup(requests.get(pageUrl).text, 'html.parser')
        #print('title:', dom.title)
        while dom:
            #print('dom:', dom)
            # Return all links in page
            for item in dom.find_all(*self._linkArgs, **self._linkAttr):
                # Apply all methods recursively zooming in to <a> element
                for z in self._zoom:
                    # print('applying', repr(z), 'to', item)
                    item = getattr(item, z[0])(*z[1])
                    # print('-->', item)
                yield item
            # Then go to next page
            dom = self.nextPage(dom)

    def nextPage(self, dom):
        """
        Go to next page
        """
        if getattr(self, '_nextPageLink', None):
            nextPageLink = dom.find('a', **self.nextPageLink)
            return '/'.join(self._baseUrl, nextPageLink['href'])
