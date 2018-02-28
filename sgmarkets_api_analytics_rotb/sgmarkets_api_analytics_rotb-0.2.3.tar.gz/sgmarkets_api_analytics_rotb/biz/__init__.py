
import numpy as np
import pandas as pd


ROUND_NB_DIGIT = 2


def vol_unit(unit):
    """
    to help express vol either in bp/day or bp/year
    """
    u = unit.upper()
    if u == 'DAY' or u == 'D':
        return 1 / 252**0.5
    else:
        return 1


def get_diff(data, start_date, end_date):
    """
    get difference between 2 dates
    """
    mask_1 = (data.index.get_level_values('date') == end_date)
    mask_2 = (data.index.get_level_values('date') == start_date)
    one = data.loc[mask_1]
    one.index = one.index.droplevel('date')
    two = data.loc[mask_2]
    two.index = two.index.droplevel('date')
    # res=res.index.droplevel('date')
    return round(one - two, ROUND_NB_DIGIT)


def get_max(data, resize=False, *args):
    """
    get max
    TBC
    """
    if resize:
        data = select_data(data, *args)
    x = data.groupby(level='expiry').apply(max)
    return round(x.reindex(data.index.get_level_values('expiry').unique(), axis=0), ROUND_NB_DIGIT)


def get_min(data, resize=False, *args):
    """
    get min
    TBC
    """
    if resize:
        data = select_data(data, *args)
    x = data.groupby(level='expiry').apply(min)
    return round(x.reindex(data.index.get_level_values('expiry').unique(), axis=0), ROUND_NB_DIGIT)


def get_surface(data, date):
    """
    get surface for given date
    TBC
    """
    mask = (data.index.get_level_values('date') == date)
    x = data.loc[mask]
    return round(drop_level(x, 'date'), ROUND_NB_DIGIT)


def select_data(data, args):
    """
    select data from dataframe
    args:
        for discrete values
            field, value1, value2, etc
        for range of values
            field, value_start, value_end, 'range'

    returns subset dataframe
    TBC
    """
    arg = args
    if arg[0] == 'date':
        if len(arg) == 4 and arg[3] == 'range':
            mask = (data.index.get_level_values(arg[0]) >= arg[1]) & (
                data.index.get_level_values(arg[0]) <= arg[2])
        else:
            mask = (data.index.get_level_values(arg[0]) == arg[1])
            for ar in arg[2:len(arg)]:
                mask = mask | (data.index.get_level_values(arg[0]) == ar)
    else:
        mask = (data.index.get_level_values(arg[0]) == arg[1])
        for ar in arg[2:len(arg)]:
            mask = mask | (data.index.get_level_values(arg[0]) == ar)

    return data.loc[mask]


def drop_level(data, index):
    """
    drop level of input dataframe - inplace
    TBC
    """
    data.index = data.index.droplevel(index)
    return data


def get_percentile(data, date, resize=False, *args):
    """
    get percentile rank from input dataframe
    TBC
    """
    if resize:
        data = select_data(data, *args)
    return get_surface(data.groupby(level='expiry').rank(pct=True), date)


def get_mean(data, resize=False, *args):
    """
    get mean
    TBC
    """
    if resize:
        data = select_data(data, *args)
    data = data.dropna()
    x = data.groupby(level='expiry').apply(np.mean)
    return round(x.reindex(data.index.get_level_values('expiry').unique(), axis=0), ROUND_NB_DIGIT)


def get_std(data, resize=False, *args):
    """
    get standard deviation
    TBC
    """
    if resize:
        data = select_data(data, *args)
    data = data.dropna()
    x = data.groupby(level='expiry').apply(np.std)
    return round(x.reindex(data.index.get_level_values('expiry').unique(), axis=0), ROUND_NB_DIGIT)


def get_z_score(data, end_dt, resize=False, *args):
    """
    get z-score
    TBC
    """
    if resize:
        data = select_data(data, *args)
    return round((get_surface(data, end_dt) - get_mean(data)) / get_std(data), ROUND_NB_DIGIT)


def build_weight(spread, weight, **kwargs):
    """
    build weight
    TBC
    """
    if (len(spread) is not len(weight)):
        if kwargs == {}:
            kwargs.setdefault('type', 'S')
        else:
            kwargs = kwargs['kwargs']

        if (len(spread) % 2 == 0 or (len(spread) % 2 == 0 and len(spread) % 3 == 0)) and (kwargs['type'].upper() != 'FLY' or kwargs['type'].upper() != 'F'):
            print('spread - weight len mismatch by default spread weighted (-1,1)')
            w = np.repeat(1, len(spread))
            pos = np.arange(1, len(w), 2)
            w[pos] = w[pos] * -1
        elif (len(spread) % 3 == 0 or (len(spread) % 2 == 0 and len(spread) % 3 == 0)) and (kwargs['type'].upper() == 'FLY' or kwargs['type'].upper() == 'F'):
            print('fly - weight len mismatch by default fly weighted (-1,2,-1)')
            w = np.repeat(-1, len(spread))
            pos = np.arange(1, len(w), 2)
            w[pos] = w[pos] * -2
    else:
        w = weight
    return w

# def build_spread(data, spread, typ_, resize=False, *args):
#     """
#     build spread
#     TBC
#     """
#     if resize:
#         data = select_data(data, args)
#     res = pd.DataFrame()
#     if typ_.upper() == "S" or typ_.upper() == "SLOPE":
#         for s in spread:
#             res[s[0] + s[1]] = data[s[1]] - data[s[0]]
#         return res
#     if typ_.upper() == "C" or typ._upper() == "CALENDAR":
#         from collections import OrderedDict
#         dic = OrderedDict()
#         for s in spread:
#             dic[(s[0] + s[1])] = data.loc[s[1]] - data.loc[s[0]]
#         res = pd.concat(dic.values(), keys=dic.keys())
#         res.index.names = ('expiry', 'date')
#         return res


def build_spread(data, spread, axis="T", weight=[], resize=False, *args, **kwargs):
    """
    build weight
    TBC
    """
    if resize:
        data = select_data(data, args)
    res = pd.DataFrame()
    w = build_weight(spread[0], weight, **kwargs)
    if axis.upper() == 'T' or axis.upper() == 'TENOR':
        for s in spread:
            nme = str()
            for i, e in enumerate(s):
                if i == 0:
                    res_tmp = data[s[i]] * w[i]
                else:
                    res_tmp = res_tmp + data[s[i]] * w[i]
                nme = nme + s[i]
            res[nme] = res_tmp
        return res

    if axis.upper() == 'E' or axis.upper() == 'EXPIRY':
        from collections import OrderedDict
        dic = OrderedDict()
        idx = data.loc[spread[0][0]].index
        col = data.loc[spread[0][0]].columns
        for s in spread:
            res_tmp = pd.DataFrame(0, index=idx, columns=col)
            nme = str()
            for i, e in enumerate(s):
                res_tmp = res_tmp + data.loc[s[i]] * w[i]
                nme = nme + s[i]
            dic[nme] = res_tmp
        res = pd.concat(dic.values(), keys=dic.keys())
        res.index.names = ('expiry', 'date')
        return res
