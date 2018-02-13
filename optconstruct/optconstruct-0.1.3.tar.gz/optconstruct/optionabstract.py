"""
    # TODO jstejska: Fill package info
"""


class OptionAbstract:
    """Option Abstract class."""

    def __init__(self, key: str, prefix: str):
        """Init.

        :param key: key value of attribute in data set
        :type key: str
        :param prefix: option prefix
        :type prefix: str
        """
        self.key = key
        self.prefix = prefix

    def satisfied(self, data: dict):
        """Check if client's option should be generated.

        :param data: data with specified option's values
        :type data: dict

        :return: True or False
        :rtype: bool
        """
        return bool(data.get(self.key, None))

    def generate(self, data, client=None):
        """Generate options.

        :param data: data with specified option's values
        :type data: dict
        :param client: client's label
        :type client: str

        :raise: NotImplementedError
        """
        raise NotImplementedError

    @staticmethod
    def _postprocessing(pattern):
        """Add additional formatting to the option.

        :param pattern:
        :type pattern: string

        :return:
        :rtype:
        """
        return pattern
