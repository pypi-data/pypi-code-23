#!/usr/env/bin python
#author: WU Dingcheng
import pandas as pd

def reader(filename):
    """
    Read the time series with specific format, two columns:
     YYYY-mm-DD, value
    :param filename: str, time series file name
    :return: pandas dateframe object
    """
    df = pd.read_csv(filename,
                     parse_dates=True,
                     names=['date', 'component'],
                     sep='\s+',
                     header=None,
                     index_col=0)

    index = df.index.to_julian_date()
    t = (index - index[0]).values
    df['t'] = t

    return df
