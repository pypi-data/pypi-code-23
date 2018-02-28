
import os

import datetime as dt
import pandas as pd

from IPython.display import Markdown

from ._util import Util


class ResponseRotbCurves:
    """
    """

    def __init__(self,
                 dic_res=None):
        """
        """
        assert isinstance(dic_res, dict), \
            'Error: dic_res must be a dict'
        assert 'curves' in dic_res, \
            'Error: curves must be a key of dic_res'

        self.dic_res = dic_res
        self.preview = Util.preview(dic_res)
        self.df_res = self._build_df_res()

    def _build_df_res(self):
        """
        """
        return pd.DataFrame(self.dic_res['curves'])

    def save_result(self,
                    folder_save='dump',
                    name=None,
                    tagged=True,
                    excel=False):
        """
        """
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        if name is None:
            name = self.__class__
        tag = ''
        if tagged:
            tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
        suffix = '.csv'
        filename = '{}{}{}'.format(name, tag, suffix)
        path = os.path.join(folder_save, filename)
        self.df_res.to_csv(path, index=None)
        print('file {} saved'.format(path))
        if excel:
            suffix = '.xlsx'
            filename = '{}{}{}'.format(name, tag, suffix)
            path = os.path.join(folder_save, filename)
            self.df_res.to_excel(path, index=None)
            print('file {} saved'.format(path))

    def _repr_html_(self):
        """
        """
        return self.df_res.to_html()

    def info(self):
        """
        """
        md = """
A ResponseRotbCurves object has the properties:
+ `dic_res`: raw response (dict)
+ `preview`: preview of raw response (string)
+ `df_res`: response data (dataframe)


and the methods:
+ `save_result()` to save the data as `.csv` and `.xlsx` files
        """
        return Markdown(md)
