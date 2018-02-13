"""
    # TODO jstejska: Fill package info
"""

from optconstruct import OptionAbstract


class ListOption(OptionAbstract):
    """List options constructor class."""

    def generate(self, data, client=None):
        """Generate options with prefix and value.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str
        :return: option
        :rtype: str
        """
        return self._msg_list_retype(data, client)

    def _msg_list_retype(self, data, client=None):
        """List or tuple transformation to consecutive parameters with prefix, separator and value.

        :param data: data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :return: options
        :rtype str
        """
        _ = client

        option = data.get(self.key, None)

        if option is None:
            return ''

        output = ""
        separator = '~'

        if not isinstance(option, (list, tuple)):
            option = [option]

        for value in option:
            if isinstance(value, int):
                output += "%s \"%s%s\" " % (self.prefix, separator, value)
            else:
                output += "%s \"%s\" " % (self.prefix, value)

        return output
