
import re
import pandas as pd

from collections import OrderedDict

from ._calendar import calendar as cal


class Util:

    @staticmethod
    def preview(data, start=200, end=200):
        """
        preview json returned by Api
        """
        string = str(data)
        n = len(string)

        if n <= start + end:
            return string

        beg, end = string[:start], string[-end:]
        res = beg + '.........({} more characters).........'.format(n) + end
        return res

    @staticmethod
    def get_unique_list(my_list):
        """
        """
        unique_list = list(OrderedDict((e, None) for e in my_list))
        unique_list = [e for e in unique_list if pd.notnull(e)]
        return unique_list

    @staticmethod
    def build_url(dic_url):
        """
        """
        return '{}{}{}'.format(dic_url['base_url'],
                               dic_url['service'],
                               dic_url['endpoint'])

    @staticmethod
    def get_list_bday_between(start_date, end_date):
        """
        """
        bd_range = pd.bdate_range(start_date,
                                  end_date,
                                  freq='C',
                                  holidays=cal.BDAY_US.holidays)
        return list(bd_range)

    @staticmethod
    def date_to_str(ts):
        """
        """
        return ts.strftime('%Y-%m-%d')

    @staticmethod
    def multiple_replace(dic, text):
        # Create a regex from the dict keys
        regex = re.compile('(%s)' % '|'.join(map(re.escape, dic.keys())))

        # For each match, lookup corresponding value in dict
        return regex.sub(lambda mo: dic[mo.string[mo.start():mo.end()]], text)
