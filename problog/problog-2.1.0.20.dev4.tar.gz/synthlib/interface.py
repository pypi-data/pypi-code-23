

class DataEncoder(object):

    def __init__(self):
        self._encodings = {}

    def to_numerical(self, table, key=None):
        """Convert categorical data to numerical.

        :param table:
        :param key: key for this part of the transformation
        :return:
        """

        encoding = self._encodings.get(key, {})

        return smart_map(encoding.encode, table)















