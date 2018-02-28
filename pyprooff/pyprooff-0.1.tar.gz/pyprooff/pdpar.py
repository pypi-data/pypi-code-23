#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submodule with functions to run pandas in parallel using ipyparallel
* distribute_unique_values <- runs a function and collects results on subsets
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import pandas as pd
import numpy as np
import ipyparallel


def _initialize():
    try:
        rc = ipyparallel.Client()
        print('Cluster of {} cores active'.format(len(rc.ids)))
    except:
        import sys
        print('Client initialization failure. Run, e.g. ipcluster start --n=4, then run function initialize()', file=sys.stderr)
        raise Exception
    return rc

def distribute_unique_values(df, distribute_col, df_function):
    """Distributes a dataframe across cluster nodes according to unique values in one column,
    then runs a function on the sub-dataframes and returns the return result of that function
    
    Arguments:
        df {pandas.DataFrame} -- dataframe to distribute
        distribute_col {str} -- name of column on which to distribute unique values
        text_function_arg_df {str} -- string representation of a function called df_function
                                      that only has one arg, (df).arg

    Returns:
        list of whatever is returned by df_function
    """
    from pyprooff.conts import split_list
    assert type(df_function) == str, 'function must be a string representation'
    rc = _initialize()
    df_to_dist = df.copy()
    df_to_dist = df_to_dist.sort_values(distribute_col)
    distribute_values = list(df_to_dist[distribute_col].unique())
    chunks = split_list(distribute_values, len(rc.ids))
    for id_, values in zip(rc.ids, chunks):
        dview = rc[id_]
        dview.block=False
        dview.execute('import pandas as pd')
        df_ = df_to_dist[df_to_dist[distribute_col].isin(values)]
        dview['df'] = df_.copy()
    dview = rc[:]
    dview.block=True
    dview.execute(df_function)
    dview.execute('coll = df_function(df)')
    colls = dview.pull('coll')
    allcolls = []
    for item in colls:
        try:
            allcolls += item
        except TypeError:
            allcolls.append(item)
    return allcolls