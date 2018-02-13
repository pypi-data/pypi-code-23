"""
    # TODO jstejska: Fill package info
"""

from optconstruct import OptionAbstract


class BasicComposed(OptionAbstract):
    """Composed options constructor class."""

    composed_keys = set()

    def satisfied(self, data: dict):
        """Check if client's option should be generated.

        :param data: data with specified option's values
        :type data: dict
        :return: True or False
        :rtype bool
        """
        self.composed_keys.add(self.key)

        return bool(set(data.keys()).intersection(self.composed_keys))

    def generate(self, data, client=None):
        """Generate options.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :raise: NotImplementedError
        """
        raise NotImplementedError

