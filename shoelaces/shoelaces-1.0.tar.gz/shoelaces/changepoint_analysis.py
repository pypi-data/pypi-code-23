import numpy as np

def detect_mean_shift( ts, B=1000):
    """ Detect mean shift in a time series. B is number of bootstrapped
        samples to draw.
    """
    x = np.arange(0, len(ts))
    stat_ts_func = compute_balance_mean_ts
    null_ts_func = shuffle_timeseries
    stats_ts, pvals, nums = get_ts_stats_significance(x, ts, stat_ts_func, null_ts_func, B=B, permute_fast=True)
    return stats_ts, pvals, nums

def compute_balance_mean( ts, t):
    """ Compute the balance. The right end - the left end."""
    """ For changed words we expect an increase in the mean, and so only 1 """
    return np.mean(ts[t + 1:]) - np.mean(ts[:t + 1])

def compute_balance_mean_ts( ts):
    """ Compute the balance at each time 't' of the time series."""
    balance = [compute_balance_mean(ts, t) for t in np.arange(0, len(ts) - 1)]
    return balance

def shuffle_timeseries( ts):
    """ Shuffle the time series. This also can serve as the NULL distribution. """
    return np.random.permutation(ts)

def get_ts_stats_significance( x, ts, stat_ts_func, null_ts_func, B=1000, permute_fast=False, label_ts=''):
    """ Returns the statistics, pvalues and the actual number of bootstrap
        samples. """
    stats_ts, pvals, nums = ts_stats_significance(
        ts, stat_ts_func, null_ts_func, B=B, permute_fast=permute_fast)
    return stats_ts, pvals, nums


def ts_stats_significance(ts, ts_stat_func, null_ts_func, B=1000, permute_fast=False):
    """ Compute  the statistical significance of a test statistic at each point
        of the time series.
    """
    stats_ts = ts_stat_func(ts)
    if permute_fast:
        # Permute it in 1 shot
        null_ts = map(np.random.permutation, np.array([ts, ] * B))
    else:
        null_ts = np.vstack([null_ts_func(ts) for i in np.arange(0, B)])
    stats_null_ts = np.vstack([ts_stat_func(nts) for nts in null_ts])
    pvals = []
    nums = []
    for i in np.arange(0, len(stats_ts)):
        num_samples = np.sum((stats_null_ts[:, i] >= stats_ts[i]))
        nums.append(num_samples)
        pval = num_samples / float(B)
        pvals.append(pval)

    return stats_ts, pvals, nums