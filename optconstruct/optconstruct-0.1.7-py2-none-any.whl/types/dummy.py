"""
    # TODO [jstejska]: Fill package info
"""

from optconstruct import OptionAbstract


class Dummy(OptionAbstract):
    """Dummy client options constructor class."""

    def __init__(self, key: str, prefix: str = ''):
        """Init.

        :param key: key value of attribute in data set
        :type key: str
        :param prefix: option prefix
        :type prefix: str
        """
        super().__init__(key, prefix)

    def satisfied(self, data: dict = ''):
        """Check if client's option should be generated.

        :param data: data with specified option's values
        :type data: dict

        :return: False
        :rtype: bool
        """
        return False

    def generate(self, data, client=None):
        """Generate dummy options only with value without prefix.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :return: option
        :rtype: str
        """
        _ = client
        _ = data
        return ''
