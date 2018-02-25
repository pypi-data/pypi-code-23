from bs4 import BeautifulSoup

try:
    import lxml
except ImportError:
    lxml = None

from crawlster.helpers.base import BaseHelper


class Content(object):
    """Content wrapper that provides common data extraction methods"""

    def __init__(self, raw_data):
        """Wraps some text or bytes to be processed"""
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode()
        self._data = raw_data
        self._parsed_data = None

    @property
    def parsed_data(self):
        """Access the underlying bs4.BeautifulSoup4 instance

        This property is provided for more advanced usage.
        """
        if not self._parsed_data:
            self._parsed_data = BeautifulSoup(self._data, 'html.parser')
        return self._parsed_data

    def css(self, pattern, get_attr=None, get_text=False):
        """Extracts data using css selector

        Returns a list of elements (as strings) with the extracted data

        Args:
            pattern (str):
                the CSS selector
            get_attr (str or None):
                if present, returns a list of the attributes of the extracted
                items
            get_text (bool):
                If should return only the content/text of the element

        Returns:
            If get_attr and get_text are not specified, returns a list of
            strings with the matches.

            If get_attr is specified, returns a list
            with the values of the specified attribute, if present. Elements
            that match the query pattern and does not have that attribute are
            ignored.

            If get_text is specified, returns a list with the text from the
            matched elements (direct children that are not nested tags).
        """
        items = self.parsed_data.select(pattern)
        if get_attr:
            return [item[get_attr] for item in items if get_attr in item.attrs]
        elif get_text:
            return [i.text for i in items]
        else:
            return [str(i) for i in items]


class ExtractHelper(BaseHelper):
    name = 'extract'

    def __init__(self):
        super(ExtractHelper, self).__init__()

    def css(self, text, selector, attr=None, content=None):
        """Extracts data using css selector.

        See :py:meth:``Content.css`` for more info.
        """
        return Content(text).css(selector, get_attr=attr, get_text=content)
