"""
    # TODO jstejska: Fill package info
"""

import copy
from optconstruct import OptionAbstract


class KWOption(OptionAbstract):
    """Dictionary options constructor class."""

    def generate(self, data, client=None):
        """Generate options with prefix and value.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str
        :return: option
        :rtype: str
        """
        return self._msg_kw_retype(data, client)

    def _msg_kw_retype(self, data, client=None):
        """Dictionary transformation to consecutive parameters with prefix, separator and value.

        :param data: data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :return: options
        :rtype str
        """
        _ = client
        option = copy.deepcopy(data.get(self.key, None))

        if option is None:
            return ''

        output = ""

        for separator in ['~', '=']:
            item = option.get(separator, None)
            if item:
                del option[separator]
                for key, value in item.items():
                    output += "%s \"%s%s%s\" " % (self.prefix, key, separator, value)

        for key, value in option.items():
            separator = '='
            if not isinstance(value, str):
                separator = '~'
            output += "%s \"%s%s%s\" " % (self.prefix, key, separator, value)

        return output
