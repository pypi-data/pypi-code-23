"""
    # TODO jstejska: Fill package info
"""

from optconstruct.optionabstract import OptionAbstract


class Argument(OptionAbstract):
    """Argument client options constructor class."""

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
        return data.get(self.key)
