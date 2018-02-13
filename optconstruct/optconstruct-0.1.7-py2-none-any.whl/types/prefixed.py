"""
    # @TODO jstejska: Fill package info
"""

from optconstruct import OptionAbstract


class Prefixed(OptionAbstract):
    """Prefixed client options constructor class."""

    def generate(self, data, client=None):
        """Generate options with prefix and value.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :return: option
        :rtype: str
        """
        _ = client
        _ = data
        option = "%s %s" % (self.prefix, data.get(self.key))
        return option
