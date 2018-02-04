"""Paragraph."""
import re

from brainlamp_toolbox import log


class Paragraph:
    """Paragraph class."""

    def __init__(self, value):
        self.value = value
        self._content = []
        self.__content_str = ""

    @property
    def value(self):
        """Get value."""
        return self._value

    @property
    def content(self):
        """Get content."""
        return self._content

    @content.setter
    def content(self, val):
        if isinstance(val, list):
            self._content = val
        elif isinstance(val, str):
            _list = val.split('\n')
            if len(_list) > 0:
                self._content = _list
            else:
                self._content = [_list]
        else:
            raise TypeError('Expected list or string')

        self.__set_content_str()

    def __set_content_str(self):
        self.__content_str = ''.join(self._content)

    @value.setter
    def value(self, val):
        if not isinstance(val, int):
            raise TypeError('Expected a integer')
        self._value = val

    @value.deleter
    def value(self):
        raise AttributeError("Can't delete attribute")

    def add_content(self, content):
        """Add content to Paragraph."""
        log.debug("Add content to %d" % self.value)
        if isinstance(content, list):
            self._content.extend(content)
        elif isinstance(content, str):
            _list = content.split('\n')
            if len(_list) > 0:
                self._content.extend(_list)
            else:
                self._content.extend([_list])
        else:
            raise TypeError('Expected list or string')

        self.__set_content_str()

    @property
    def words(self):
        """List of words."""
        return re.findall(r'\w+', self.__content_str)

    @property
    def count_words(self):
        """Count of words."""
        return len(self.words)

    @property
    def count_lines(self):
        """Count lines."""
        return len(self._content)

    @property
    def sentences(self):
        """List of sentences."""
        return self.__content_str.split('.')

    @property
    def count_sentences(self):
        """Count sentences."""
        return len(self.sentences)

    def __repr__(self):
        """Represent Paragraph."""
        return 'Paragraph({!r})'.format(self._value)

    def __str__(self):
        return self.__content_str

    def __iter__(self):
        """Iterate content."""
        return iter(self.content)
