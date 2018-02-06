
import os
import copy
import functools

import datetime as dt
import pandas as pd

from IPython.display import Markdown
from dateutil.parser import parse

from ._util import Util
from .response_rotb_compute_strategy_components import ResponseRotbComputeStrategyComponents


class SliceRotbComputeStrategyComponents:
    """
    """

    def __init__(self,
                 obj_res,
                 x=None,
                 y=None,
                 z=None,
                 dic_req_fix=None,
                 value=None,
                 y_pos='index',  # index or column
                 ):
        """
        """
        # print(type(obj_res))
        assert isinstance(obj_res, ResponseRotbComputeStrategyComponents), \
            'Error: obj_res must be a ResponseRotbComputeStrategyComponents object'
        self.res = obj_res
        self.y_pos = y_pos

        msg1 = 'Error: {} must be a column name in df_req'
        msg1b = 'Error: y_pos must be a "index" or "column"'
        msg2 = 'z must be None if y is None'
        msg3 = 'Error: dic_req_fix must be a dict'
        msg4 = 'Error: {} is not a column of df_req'
        msg5 = 'Error: {} has {} values - Must be one'
        msg6 = 'Error: value must be a column of df_res'
        msg7 = 'Error: {} is present in dic_req_fix'
        msg8 = 'Error: {} has {} values in dic_res_param - Must be one'

        assert x in self.res.df_req.columns, msg1.format('x')
        if y:
            assert y in self.res.df_req.columns, msg1.format('y')
            assert y_pos in ['index', 'column'], msg1b
        if x and y:
            if z is not None:
                assert z in self.res.df_req.columns, msg1.format('z')
        else:
            assert z is None, msg2

        assert isinstance(dic_req_fix, dict), msg3

        # transform
        for k, v in dic_req_fix.items():
            if isinstance(v, pd.Timestamp):
                v = Util.date_to_str(v)
                dic_req_fix[k] = v
            if isinstance(v, (str, int, float)):
                dic_req_fix[k] = [v]

        for k, v in dic_req_fix.items():
            assert k in self.res.df_req.columns, msg4.format(k)
            assert len(v) == 1, msg5.format(k, len(v))

        assert value in self.res.df_res.columns, msg6

        li_req_fix = list(dic_req_fix.keys())
        li_req_sel = copy.deepcopy(li_req_fix)
        li_xyz = [e for e in [x, y, z] if e is not None]
        for v in li_xyz:
            li_req_sel.append(v)
            assert v not in li_req_fix, msg7.format(v)
        # display(li_xyz)

        dic_req_param_full = copy.deepcopy(dic_req_fix)
        # display(dic_req_fix)
        dic_req_param_full = {k: v[0] for k, v in dic_req_param_full.items()}
        # display(dic_req_param_full)

        for c in self.res.df_req.columns:
            if c not in li_req_sel:
                v = self.res.dic_req_param[c]
                assert len(v) == 1, \
                    msg8.format(k, len(self.res.dic_res_param))
                dic_req_param_full[c] = v[0]

        # display(dic_req_param_full)
        li_mask = []
        for k, v in dic_req_param_full.items():
            # EXCEPTION
            if k != 'nominal':
                li_mask.append(self.res.df_req[k] == v)
        # display(li_mask)
        mask = functools.reduce((lambda x, y: x & y),
                                li_mask)

        df_slice = pd.concat([self.res.df_req[li_xyz],
                              self.res.df_res[value]], axis=1)
        # display(df_slice)
        df_slice = df_slice.loc[mask]
        self.df_slice = df_slice.reset_index(drop=True)

        self.df_pivot = None

        if len(li_xyz) == 1:
            df_pivot = df_slice[[x, value]]
            df_pivot = df_pivot.set_index(x)
            df_pivot = df_pivot.loc[self.res.dic_req_param[x]]

        if len(li_xyz) == 2:
            # display(df_slice)
            df_pivot = df_slice.pivot_table(index=x,
                                            columns=y,
                                            values=value)
            # display(df_pivot)
            df_pivot = df_pivot.loc[self.res.dic_req_param[x],
                                    self.res.dic_req_param[y]]

        if len(li_xyz) == 3:
            df_pivot = df_slice[[x, y, z, value]]
            if self.y_pos == 'index':
                df_pivot = df_pivot.pivot_table(index=[x, y],
                                                columns=z,
                                                values=value)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[x],
                                            axis=0,
                                            level=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[y],
                                            axis=0,
                                            level=1)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[z],
                                            axis=1)
            if self.y_pos == 'column':
                df_pivot = df_pivot.pivot_table(index=x,
                                                columns=[y, z],
                                                values=value)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[x],
                                            axis=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[y],
                                            axis=1,
                                            level=0)
                df_pivot = df_pivot.reindex(self.res.dic_req_param[z],
                                            axis=1,
                                            level=1)

        self.df_pivot = df_pivot

    def save(self,
             folder_save='dump',
             name=None,
             tagged=True,
             excel=False):
        """
        """
        if not os.path.exists(folder_save):
            os.makedirs(folder_save)
        if name is None:
            name = 'pivot'
        tag = ''
        if tagged:
            tag = dt.datetime.now().strftime('_%Y%m%d_%H%M%S')
        suffix = '.csv'
        filename = '{}{}{}'.format(name, tag, suffix)
        path = os.path.join(folder_save, filename)
        self.df_pivot.to_csv(path, index=None)
        print('file {} saved'.format(path))
        if excel:
            suffix = '.xlsx'
            filename = '{}{}{}'.format(name, tag, suffix)
            path = os.path.join(folder_save, filename)
            self.df_pivot.to_excel(path, index=None)
            print('file {} saved'.format(path))

    def _repr_html_(self):
        """
        """
        return self.df_slice.to_html()

    def info(self):
        """
        """
        md = """
A SliceRotbComputeStrategyComponents object has the following properties:
+ `df_slice`: dataframe extracted from the postprocess dataframe `df_set` so that:
    + No constraints on params `x`, `y` (if input), `z` (if input)
    + All other request params are kept only if their value match the `dic_req_fix` dictionary of fixed values
        + All request params not `x` or `y` or `z` having more than one value must be specified in `dic_req_fix`
    + Only the response param `value` is kept

+ `df_pivot`: dataframe extracted from `df_slice`. It can be of dimension:
+ 1 if only `x` is defined
+ 2 if `x`and `y` are defined
+ 3 if `x`and `y` and `z` are defined
    + If the dimension is 3 and `y_pos` is `index` then (`x`, `y`) are a dataframe row multi-index
    + If the dimension is 3 and `y_pos` is `column` then (`y`, `z`) are a dataframe column multi-index
        """
        return Markdown(md)
