
import re
import pandas as pd

from collections import OrderedDict


class Util:

    @staticmethod
    def multiple_replace(dic, text):
        # Create a regex from the dict keys
        regex = re.compile('(%s)' % '|'.join(map(re.escape, dic.keys())))

        # For each match, lookup corresponding value in dict
        return regex.sub(lambda mo: dic[mo.string[mo.start():mo.end()]], text)
