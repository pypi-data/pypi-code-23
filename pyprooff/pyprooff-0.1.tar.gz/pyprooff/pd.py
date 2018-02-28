#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def print_helpers():
    print('pd.options.mode.chained_assignment = None  # CAREFUL\n'
          "pd.set_option('display.max_rows', 30)\n"
          "pd.set_option('expand_Frame_repr', False))")

def df_delta_v1(df, sort_col, on_change_col='index', ignore_cols=None,
             omit_first=False):
    """
    Prints only changes in values in a dataframe from snapshotted row to
    snapshotted row, which may be every row if desired

    Args:
        df: dataframe to be analyzed
        sort_col: str, column by which to sort dataframe
        on_change_col: str; column name or 'index'
                       changes since last snapshot will be printed
                       whenever the value in this column changes from the
                       previous row. If there is a column named 'index', the
                       actual index will be used instead



    Prints row by row changes in a dataframe when sorted by sort_col, whenever
    the value of on_change_col (or the index, if left to default -- careful,
    it may break if there is a column called index) changes. Rest
    self-explanatory."""
    df = df.sort_values(sort_col)
    last = {k: None for k in list(df.columns)}
    last_change_val = None
    for i, (idx, row) in enumerate(df.iterrows()):
        print('index: {}'.format(idx))
        if on_change_col == 'index':
            increment = True
        else:
            if i == 0 or row[on_change_col] != last_change_val:
                increment = True
                last_change_val = row[on_change_col]
                print('  {}: {}'.format(on_change_col, last_change_val))
        if increment:
            for col in row.index:
                if ignore_cols is None or col not in ignore_cols:
                    if col != on_change_col:
                        if i == 0 and not omit_first:
                            print('    {}: {}'.format(col, row[col]))
                        elif (not(pd.isnull(row[col]) and pd.isnull(
                              last[col])) and row[col] != last[col]):
                            print('    {}: {} --> {}'.format(col,
                                                             last[col],
                                                             row[col]))
                        last[col] = row[col]

def df_delta_v2(df, sort_col=None, on_change_col='index', ignore_cols=None,
             ignore_threshold=None, omit_first=False,
             always_print_index=False, debug=False,
             renumber_index=False):
    """
    Prints only changes in values in a dataframe from snapshotted row to
    snapshotted row, which may be every row if desired

    Args:
        df: dataframe to be analyzed
        sort_col: str, column by which to sort dataframe.
                  if None, df is taken to be already sorted
        on_change_col: str; column name or 'index'
                       changes since last snapshot will be printed
                       whenever the value in this column changes from the
                       previous row. If there is a column named 'index', the
                       actual index will be used instead.
        ignore_cols: list, columns to be left out of the comparison
        ignore_threshold: float from 0 to 1, only columns that change less often than
                          (not equal to) this will be reported; e.g. if ignore_threshold=1,
                          any columns that change every time on_change_col times will
                          be ignored.
        omit_first: if False, the first value will show all columns of the dataframe
                    with their initial values. if True, print results will start with
                    first row with a non-ignored change.
        always_print_index: if True, will show every row change, even if it includes
                            no on_change_col change and thus nothing to report.
        debug: if True, prints a bunch of intermediate values
        renumber_index: if True, uses iloc for loc in index

    Returns:
        None (just prints), unless debug=True, then returns list of print results
    """
    from collections import defaultdict
    def dprint(message, value=None):
        if debug:
            if value is None:
                print('*** {}'.format(message))
            else:
                print('*** {}: {}'.format(message, value))
    # changes in change_col are numbered invisibly to user
    # curr_change_count counts those changes
    # change_counter counts how many column changes are at each such change
    # after results are collected, ignore_threshold may reduce change_counter
    # and end up with changes being omitted afterwards when printing
    curr_change_count = 0
    change_counter = defaultdict(int)  # change_count: #
    col_changes = defaultdict(int)  # column: number
    to_print = [] # tuple of change_counter, column, report
    if sort_col is not None:
        dprint('sorted by', sort_col)
        df = df.sort_values(sort_col)
    if renumber_index:
        df = df.reset_index(drop=True)
    # store last seen values
    last = {k: None for k in list(df.columns)}
    last_change_val = None
    for i, (idx, row) in enumerate(df.iterrows()):
        dprint('idx', idx)
        if on_change_col == 'index':
            increment = True
            curr_change_count += 1
            to_print.append([curr_change_count, '_index', 'index: {}'.format(idx)])
            dprint("added index because it's change col")
        else:
            if always_print_index:
                to_print.append([curr_change_count, '_index', 'index: {}'.format(idx)])
                dprint("added index because always_print_index")
            if i == 0 or not equalorbothnull(on_change_col, last_change_val):
                increment = True
                curr_change_count += 1
                last_change_val = row[on_change_col]
#                 if always_print_index:
#                     to_print.append([curr_change_count, '_index', 'index: {}'.format(idx)])
                to_print.append([curr_change_count, '_on_change', '  {}: {}'.format(on_change_col, last_change_val)])
                dprint('added change col')
        if increment:
            for col in row.index:
                if ignore_cols is None or col not in ignore_cols:
                    if col != on_change_col:
                        if i == 0:
                            if not omit_first:
                                to_print.append([curr_change_count, 'first', '    {}: {}'.format(col, row[col])])
                                dprint('added col because i==0', col)
                            last[col] = row[col]
                        elif not equalorbothnull(row[col], last[col]):
                            to_print.append([curr_change_count, col, '    {}: {} --> {}'.format(col,
                                                             last[col],
                                                             row[col])])
                            dprint('added col because change', col)
                            change_counter[curr_change_count] += 1
                            col_changes[col] += 1
                            last[col] = row[col]
    cols_to_ignore = []
    if ignore_threshold is None:
        new_to_print = to_print
    else:
        for col, num in col_changes.items():
            if num >= curr_change_count * ignore_threshold:
                cols_to_ignore.append(col)
        # decrement counter wherever cols_to_ignore member appears
        new_to_print = []
        for change_num, type_, message in to_print:
            if type_ not in cols_to_ignore:
                new_to_print.append([change_num, type_, message])
            else:
                change_counter[change_num] -= 1
                dprint('change_counter{} decremented to {}'.format(change_num, change_counter[change_num]))
    dprint('cols_to_ignore', cols_to_ignore)
    to_really_print = []
    for change_num, type_, message in new_to_print:
        if change_counter[change_num] > 0:
            to_really_print.append(message)
    if debug:
        return to_really_print
    else:
        for item in to_really_print:
            print(item)

def df_factor_iter(df, factor_col, df_func, togo=False, *args):
    """
    Quickly iterates over subsets of dataframe based on every value of
    factor_col, and performs df_func function on that smaller dataframe

    Args:
        df: a pandas DataFrame
        factor_col: string, the name of a column containing factors
        df_func: a function that takes the subsetted dataframe as first argument
        togo: whether to use the pyprooff.perf Togo class
        *args: other arguments that will be passed to df_func

    Returns:
        dict of factor values: output of df_func
    """

    if togo:
        from pyprooff.perf import Togo

    import pandas as pd
    import numpy as np

    result = {}
    df = df.sort_values(factor_col)
    unique_factors = list(df[factor_col])
    factor_array = np.array(list(df[factor_col]))
    # Determine the maximum possible number of rows for a factor value
    # the +1 probably isn't necessary, but I'm paranoid
    max_rows = df[factor_array].value_counts()[0] + 1

    if togo:
        looper = Togo(unique_factors, 1, 100)

        ### in prog
        togo = Togo(ucids, 1, 20)
        curr_pos = 0
        for cid in ucids:
            #togo.loop()
            vect = vcids[curr_pos:curr_pos+max_rows]
            masklen = (vect == cid).sum()
            dfsub = df_[curr_pos:curr_pos+masklen]
            break

def equalorbothnull(a, b):
    """Returns True if a == b, including when both a and b are NaN"""
    if a == b:
        return True
    elif pd.isnull(a) and pd.isnull(b):
        return True
    else:
        return False

def df2dict(df, key_col, val_col, must_be_unique=True):
    """
    Turns a DataFrame into a dict, with one column as key and another
    as value.

    Args:
    df: pandas.DataFrame
    key_col: str, name of column to use as key
    val_col: str, name of column to use as value
    must_be_unique: bool, default True, if True will raise KeyError
                    if not all values in key_col are distinct
                    If false, the values associated with each key
                    will be the bottommost appearing.

    Returns:
    dict
    """
    if must_be_unique:
        try:
            assert len(df) == len(df[key_col].unique())
        except:
            raise KeyError('key_col does not have unique values')
    return df[[key_col, val_col]]\
           .set_index(key_col, drop=True)\
           .to_dict()\
           [val_col]


def describe_pd_object(data):
    """
    An enhancement of pandas .describe() method, especially showing
    number of nulls and unique values.

    Args:
        data: a pandas series or dataframe

    Returns:
        None

    Prints:
        A description

    Example:
        >>> df = pd.DataFrame({'a': [0,1,2,3,4,5]})
        >>> describe_pd_object(df)
        1 columns: ['a']

        Name:    a
        Length:  6
        Null:    0
        Uniques: 6
        Row/Uniq:1.0
        Zero:    1
        nMin:    1
        nMax:    1
        count    6.000000
        mean     2.500000
        std      1.870829
        min      0.000000
        25%      1.250000
        50%      2.500000
        75%      3.750000
        max      5.000000
        Name: a, dtype: float64
    """

    import pandas as pd
    if type(data) == pd.core.frame.DataFrame:
        to_do = [data[col] for col in data.columns]
        return_string = ['{} columns: {}'.format(len(data.columns),
                                                 list(data.columns)),
                         '']
    elif type(data) == pd.core.series.Series:
        to_do = [data]
        return_string = []
    else:
        raise TypeError('data must be pandas series or dataframe')
    for i, series in enumerate(to_do):
        if i > 0:
            return_string.append('')
        uniques = len(series.unique())
        length = len(series)
        for item in ['Name:    {}'.format(series.name),
                     'Length:  {}'.format(length),
                     'Null:    {}'.format(sum(pd.isnull(series))),
                     'Uniques: {}'.format(uniques),
                     'Row/Uniq:{}'.format(round(length*1./uniques, 1)),
                     'Zero:    {}'.format(sum(series == 0)),
                     'nMin:    {}'.format(sum(series == series.min())),
                     'nMax:    {}'.format(sum(series == series.max())),
                     repr(series.describe())]:
            return_string.append(item)
    print('\n'.join(return_string))


def concat_from_glob(pattern):
    """
    Reads a glob pattern for files and compiles them into
    a single dataframe with a usual serial index

    Args:
        pattern: glob pattern, e.g. foldern?/my*.csv
                 The extension must be 'csv' or 'pickle'

    Returns:
        pandas dataframe

    Prints:
        number of files found in glob
    """
    import glob
    import pandas as pd
    ext = pattern.split('.')[-1]
    assert ext in ['csv', 'pickle'], 'glob pattern must end with "csv" or "pickle"'
    fps = glob.glob(pattern)
    print('{} files found.'.format(len(fps)))
    df = pd.DataFrame()
    for fp in fps:
        if ext == 'csv':
            df_ = pd.read_csv(fp)
        elif ext == 'pickle':
            df_ = pd.read_pickle(fp)
        df = pd.concat([df, df_])
    df = df.reset_index(drop=True)
    return df


def value_counts_df_sorted_ties(df, column):
    """returns DataFrame of value_counts with ties sorted
    I have a feeling this doesn't work"""
    vc = pd.DataFrame(df[column].value_counts()).reset_index(drop=False).sort_values([column, 'index'],
                      ascending=[False, True]).set_index('index', drop=True)
    return vc



def find_col(df, pattern, regex=False, case_sensitive=False,
             to_return=False):
    """looks in column names of pandas dataframe ``df`` for those
    that match ``pattern``, using regex or string.find,
    prints result or returns list. Either way number of
    matches is printed"""
    columns = list(df.columns)
    result = []
    for col in columns:
        if regex:
            import re
            if case_sensitive:
                if re.search(pattern, col):
                    result.append(col)
            else:
                if re.search(pattern, col, re.IGNORECASE):
                    result.append(col)
        else:
            if case_sensitive:
                if col.find(pattern) != -1:
                    result.append(col)
            else:
                if col.lower().find(pattern) != -1:
                    result.append(col)
    if to_return:
        print('{} matches found out of {}'.format(len(result), len(columns)))
        return result
    else:
        print('{} matches found out of {}:'.format(len(result), len(columns)))
        # ^ extra colon
        for match in result:
            print(match)



def flatten_multicolumn(df, join_str='_', preserve_blanks=False,
                        reset_multi_index=True):
    """Takes a pandas DataFrame, df, and returns a dataframe with a
    one-level index,
    preserving names. For example, if the first column of a dataframe
    has column names
    level 0 = 'income', level 1 = 'median', and join_str == '_', the
    column in the
    returned dataframe will be 'income_median'.

    ARGS:
      df: a pandas DataFrame
      join_str: the string(of any length) used to join the names of a column
      preserve_blanks: if False, will omit join_str when a name level is blank.
                       For example, if the levels of a column name are ['a', ''],
                       preserve_blanks=True will return 'a_' while
                       preserve_blanks=False will return 'a'
      reset_index: after columns are flattened, flattens and resets index only if
                   it is multilevel (user will be warned)

    Note: if df's columns are not multilevel, no changes to columns will
     be made, and
          user will be notified; same for index if reset_multi_index=True"""

    if str(type(df.columns)).find('MultiIndex') == -1:
        print('Columns are not MultiIndex. No change to columns')
    else:
        new_colnames = []
        levels = list(df.columns.levels)
        num_levels = len(levels)
        labels = list(df.columns.labels)
        for colnum in range(len(labels[0])):
            for levelnum in range(num_levels):
                if levelnum == 0:
                    colname = levels[levelnum][labels[levelnum][colnum]]
                else:
                    addition = levels[levelnum][labels[levelnum][colnum]]
                    if preserve_blanks or len(addition) > 0:
                        addition = join_str + addition
                        colname = colname + addition
            new_colnames.append(colname)
        while num_levels > 1:
            df.columns = df.columns.droplevel(num_levels - 1)
            num_levels -= 1
        df.columns = new_colnames
    if reset_multi_index:
        if str(type(df.index)).find('MultiIndex') == -1:
            print('Index is not MultiIndex. No change to index')
        else:
            df = df.reset_index(drop=False)
    return df

def normalize_col(df, colname, newname, ignore_nan=False):
    """normalizes every value in a pandas dataframe column by subtracting
     the mean and
    dividing by the standard deviation. If there are any missing values
     in the column,
    it will return all NaNs unless ignore_nan==True, in which case the
     mean and standard
    deviation are calculated without missing values, and only missing
     values will return
    NaN. Returns a new dataframe with a column based on newname;
     if newname == colname,
    colname will be overwritten. If newname has {}, colname will
     be substituted, e.g. if
    colname == 'income' and newname == '{}_normalized', newname
     will be 'income_normalized'
    """
    assert df[colname].dtype != 'O', "Column {} must be numeric".\
           format(colname)
    def normalize(value, mean, std):
        return (value - mean) / std
    if ignore_nan:
        series = df[colname].dropna()
    else:
        series = df[colname]
    mean = series.mean()
    std = series.std()
    if newname.find('{}') != -1:
        newname = newname.replace('{}', colname)
    df[newname] = df[colname].apply(normalize, args=(mean, std))

def value_counts_sorted(df, column, to_return=False):
    """Gives value counts of dataframe column, sorted.
    If to_return == False, just prints to stdout"""
    import pandas as pd
    dftemp = pd.DataFrame(df[column].value_counts())
    dftemp.sort(inplace=True)
    dftemp.columns = [column]
    print(dftemp)
    if to_return:
        return dftemp

def rescale_col(df, colname, newname, ignore_nan=False):
    """rescales every value in a pandas dataframe column from 0 to 1 based on value,
    not rank. If there are any missing values in the column,
    it will return all NaNs unless ignore_nan==True, in which case the min and max
    are calculated without missing values, and only missing values will return
    NaN. Returns a new dataframe with a column based on newname; if newname == colname,
    colname will be overwritten. If newname has {}, colname will be substituted, e.g. if
    colname == 'income' and newname == '{}_rescaled', newname will be 'income_rescaled'
    """
    assert df[colname].dtype != 'O', "Column {} must be numeric".format(colname)
    def rescale(value, min_, max_):
        return (value - min_) / (max_ - min_)
    if ignore_nan:
        series = df[colname].dropna()
    else:
        series = df[colname]
    max_ = series.max()
    min_ = series.min()
    if newname.find('{}') != -1:
        newname = newname.replace('{}', colname)
    df[newname] = df[colname].apply(rescale, args=(min_, max_))
    return df

def to_csv_int_nansafe(df, *args, **kwargs):
    """Write `df` to a csv file, allowing for missing values
    in integer columns

    Uses `_lost_precision` to test whether a column can be
    converted to an integer data type without losing precision.
    Missing values in integer columns are represented as empty
    fields in the resulting csv.

    from:
    http://stackoverflow.com/a/31208873
    """

    EPSILON = 1e-9

    def _lost_precision(s):
        """The total amount of precision lost over Series `s`
        during conversion to int64 dtype
        """
        try:
            return (s - s.fillna(0).astype(np.int64)).sum()
        except ValueError:
            return np.nan

    def _nansafe_integer_convert(s):
        """Convert Series `s` to an object type with `np.nan`
        represented as an empty string ""
        """
        if _lost_precision(s) < EPSILON:
            # Here's where the magic happens
            as_object = s.fillna(0).astype(np.int64).astype(np.object)
            as_object[s.isnull()] = ""
            return as_object
        else:
            return s

    df.apply(_nansafe_integer_convert).to_csv(*args, **kwargs)


def harmonize_column_types(df, columns='all', nan_int_value=-1):
    """Returns dataframe with the following changes:
    1. If column dtype is float and all non-null values are integers,
       nulls are replaced with nan_int_value and column is converted to integer
    2. If column dtype is object and at least one item is of type str,
       nulls are replaced with nan_int_value and then all items are
       coerced to type str

    columns = 'all', or one column name (which can't be 'all'),
    or list of column names
    """
    assert type(nan_int_value) == int
    df_ = df.copy()
    if columns == 'all':
        columns = list(df_.columns)
    else:
        from six import string_types
        if isinstance(columns, string_types):
            columns = [columns]

    if nan_int_value in df_.values:
        raise ValueError("{} is used as a value in DataFrame".format(nan_int_value))
    elif str(nan_int_value) in df_.values:
        raise ValueError("'{}' is used as a value in DataFrame".format(nan_int_value))
    def maybe_int(number):
        try:
            if number == int(number):
                return True
            else:
                return False
        except:
            return False
    for col in df_.columns:
        if col in columns:
          if df_[col].dtype == float:
              # check if all non-null values can be expressed as int
              if all(df_[col].dropna().apply(maybe_int)):
                  df_.loc[:, col] = df_.loc[:, col].fillna(nan_int_value).astype(np.int64)
          elif df_[col].dtype == 'O':
              # check if any value is a string
              if any(df_[col].apply(lambda x: type(x) == str)):
                  df_.loc[:, col] = df_.loc[:, col].fillna(str(nan_int_value))
                  df_.loc[:, col] = df_.loc[:, col].apply(lambda x: str(x))
    return df_

def print_quantiles(df, columns, start_numerator=0, end_numerator=None, step=1, denominator=100,
                    to_return=False):
    """Prints equally-spaced quantiles starting from start_numerator / denominator, to
    end_numerator / denominator (inclusive; 1 if end_numerator is None).
    Columns can be string of single column name.
    if to_return, returns df; otherwise, prints."""
    from six import string_types
    if isinstance(columns, string_types):
        columns = [columns]
    if end_numerator is None:
        end_numerator = denominator
    collector = []
    colnames = ['quantile']
    lend = len(str(denominator))
    for col in columns:
        colnames += [col[:5], 't'+col[:5]]
    for i in range(start_numerator, end_numerator+1, step):
        row = []
        num = str(i)
        nspaces = lend - len(num)
        num = ' '*nspaces+num
        row.append('{}/{}'.format(num, denominator))
        for col in columns:
            row.append(round(df[col].quantile(i/100.0),3))
            row.append(round(df[col].quantile(i/100.0)/df[col].max(),3))
        collector.append(row)
    df_ = pd.DataFrame(collector, columns=colnames)
    if to_return:
        return df_
    else:
        pd.set_option('display.max_rows', 112)
        pd.set_option('expand_Frame_repr', False)
        print(df_)


def weighted_quantile(values, weights, quantile=0.5):
    df_ = pd.DataFrame({'val': values, 'weight': weights})
    df_['weight_cumsum'] = df_.weight.cumsum()
    cutoff = df_.weight.sum() * quantile
    return df_[df_.weight_cumsum >= cutoff].val.iloc[0]


def sample_within_field(df, col, length, err_to_more=False):
    """
    samples a dataframe to return a new dataframe of length ``length``, but keeping
    all rows with the same value in the column ``col`` intact.

    Args:
        df: <pandas DataFrame>
        col: <str> the column name to keep intact
        length: <int> the length of the returned DataFrame (approx.)
        err_to_more: <bool> Keeping the column intact means it may not be possible
                     to return a dataframe of length exactly equal ``length``.
                     if err_to_more is True, the returned DataFrame may be longer
                     than ``length``; if False, the returned DataFrame will be of
                     length at most ``length``.

    Returns:
         a pandas DataFrame of length approx. ``length``.
    """
    import pandas as pd
    from collections import Counter
    from random import choice
    c = Counter(list(df[col]))
    lst = list(df[col])
    remaining = length
    to_keep = set()
    while remaining > 0:
        instance = choice(lst)
        num_inst = c[instance]
        remaining -= num_inst
        lst = [x for x in lst if x != instance]
        if err_to_more or remaining >= 0:
            to_keep.add(instance)
    return df[df[col].isin(to_keep)]