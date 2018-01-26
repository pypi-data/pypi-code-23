from six.moves.urllib.parse import urlparse
from ..errors import InvalidURL


class URL(object):
    """Validate that value is a well formed URL"""
    def __init__(self, schemes=None):
        """
        Args:
            schemes (set): a set of allowed schemes
        """
        self._schemes = schemes

    def __call__(self, value, path):
        """Validate URL format of value

        Args:
            value (object): value to validate
            path (list): error path
        """
        result = urlparse(value)
        if self._schemes and result.scheme not in self._schemes or\
                not (result.scheme and result.netloc):
            raise InvalidURL(value, path=path)
