import pandas as pd


def add_fake_byvars(df, data_multipler_per_byvar=2, num_byvars=1, byvar_basename='byvar'):
    """
    WARNING: do not use when index is important. index will be dropped.

    Duplicates data and creates a new variables in each copy of the data. Then combines the two
    so that the new dataset is twice the size, with repeated data except for one new variable
    which just says which duplicated dataset it came from.

    Then if num_byvars > 1, does the above repeatedly, creating new byvars. The total data
    size will be n * data_multipler_per_byvar ^ num_byvars

    Useful for performance testing when a function does something in groups by a variable.
    """

    for i in range(num_byvars):
        df = _add_fake_byvar(df, data_multipler=data_multipler_per_byvar, byvar_name=byvar_basename)

    return df

def _add_fake_byvar(df, data_multipler=2, byvar_name='byvar'):
    """
    WARNING: do not use when index is important. index will be dropped.

    Duplicates data and creates a new variable in each copy of the data. Then combines the two
    so that the new dataset is twice the size, with repeated data except for one new variable
    which just says which duplicated dataset it came from.

    Useful for performance testing when a function does something in groups by a variable.
    """
    df_dups = [df.copy() for i in range(data_multipler)]
    byvar_name = _set_byvar_name(df.columns, byvar_name=byvar_name)

    out_df = pd.DataFrame()
    for i, temp_df in enumerate(df_dups):
        temp_df[byvar_name] = i
        out_df = out_df.append(temp_df)

    return out_df.reset_index(drop=True)


def _set_byvar_name(cols, byvar_name='byvar', i=0):

    if i == 0:
        # try original before adding index
        new_byvar_name = byvar_name
    else:
        new_byvar_name = f'{byvar_name}{i}'

    if new_byvar_name in cols:
        i += 1
        return _set_byvar_name(cols, byvar_name=byvar_name, i=i)
    else:
        return new_byvar_name