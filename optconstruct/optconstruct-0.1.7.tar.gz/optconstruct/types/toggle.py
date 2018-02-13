"""
    # @TODO jstejska: Fill package info
"""

from optconstruct import OptionAbstract


class Toggle(OptionAbstract):
    """Toggle client options constructor class."""

    def generate(self, data, client=None):
        """Generate toggle options with prefix only.

        :param data: data with specified option's values
        :type: dict
        :param client: client's label
        :type client: str

        :return: option
        :rtype: str
        """
        _ = client
        _ = data
        return self.prefix

