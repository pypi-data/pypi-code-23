import numpy as np
import pandas as pd


def calculate_znorm(series, mode="global", **kwargs):
    znorm = np.array([np.nan] * len(series))
    if len(series.value_counts(dropna=True).index) > 1:

        # Detect the z-norm outliers
        if mode not in ["rolling", "global"]:
            raise Exception("Not valid mode in detect_znorm_outliers. "
                            "Only 'rolling' or 'global' are available")
        if mode == "global":
            znorm = np.abs((series - series.mean()) / series.std(ddof=0))
        elif mode == "rolling":
            if 'window' in kwargs:
                mean_vals = series.rolling(center=True, window=kwargs['window'], min_periods=1).mean()
                std_vals = series.rolling(center=True, window=kwargs['window'], min_periods=1).std(ddof=0)
                znorm = np.abs((series - mean_vals) / std_vals).as_matrix()
            else:
                raise Exception("Window not specified for 'rolling' mode. Specify a window")
    return znorm


def detect_min_threshold_outliers(series, threshold):
    bool_outliers = series < threshold
    return bool_outliers


def detect_znorm_outliers(series, threshold, mode="global", **kwargs):
    znorm = calculate_znorm(series, mode, **kwargs)
    bool_outliers = (znorm > threshold)
    return bool_outliers


def detect_max_threshold_outliers(series, threshold):
    bool_outliers = series > threshold
    return bool_outliers


def detect_outliers(series, threshold, method, **kwargs):
    bool_outliers = np.array([False]*len(series))
    for meth, thres in zip(method, threshold):
        if meth == 'znorm':
                bool_outliers_method = detect_znorm_outliers(series, thres, **kwargs)
        elif meth == 'max_threshold':
            bool_outliers_method = detect_max_threshold_outliers(series, thres)
        elif meth == 'min_threshold':
            bool_outliers_method = detect_min_threshold_outliers(series, thres)
        else:
            raise Exception("Specified method not implemented"
                            "Available methods are 'znorm', 'max_threshold', 'min_threshold'")
        bool_outliers = np.logical_or(bool_outliers, bool_outliers_method)
    return bool_outliers


def clean_series(series, bool_outliers):
    cleaned_series = series.copy()
    cleaned_series[bool_outliers==True] = np.nan
    return cleaned_series


def percentage_of_gaps(series):
    try:
        ratio_nans = round((float(series.value_counts(dropna=False)[np.nan]) / float(len(series))) * 100.0, 2)
    except ZeroDivisionError:
        ratio_nans = 0.0

    return ratio_nans


def summary(series, **kwargs):
    dict_return = {
        "dateStart": min(series.index),
        "dateEnd": max(series.index),
        "frequency": (pd.Series(series.index[1:]) - pd.Series(series.index[:-1])).value_counts().index[0],
        "mean": np.nanmean(np.array(series)),
        "sd": np.nanstd(np.array(series)),
        "min": np.nanmin(np.array(series)),
        "max": np.nanmax(np.array(series)),
        "p1": np.nanpercentile(np.array(series), 1, interpolation='linear'),
        "p5": np.nanpercentile(np.array(series), 5, interpolation='linear'),
        "p25": np.nanpercentile(np.array(series), 25, interpolation='linear'),
        "p50": np.nanpercentile(np.array(series), 50, interpolation='linear'),
        "p75": np.nanpercentile(np.array(series), 75, interpolation='linear'),
        "p95": np.nanpercentile(np.array(series), 95, interpolation='linear'),
        "p99": np.nanpercentile(np.array(series), 99, interpolation='linear')
    }
    dict_return.update(kwargs)