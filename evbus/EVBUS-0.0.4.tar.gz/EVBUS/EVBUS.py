#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File:      EVBUS.py
# @Author:    Li Yao
# @Created:   20/02/2018 12:48 AM
"""
This file contains the class EVBUS, which is an implementation of:
@article{Mentch2016,
author = {Mentch, Lucas and Hooker, Giles},
doi = {10.1080/10618600.2016.1256817},
journal = {Journal of Machine Learning Research},
keywords = {bagging,random forests,subbagging,trees,u-statistics},
number = {1},
pages = {1--41},
title = {{Quantifying Uncertainty in Random Forests via Confidence Intervals and Hypothesis Tests}},
volume = {17},
year = {2016}
}
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import multiprocessing
from multiprocessing import cpu_count

sub_version = np.__version__.split('.')
if int(sub_version[0]) == 1 and int(sub_version[1]) <= 8:
    # Required to be greater than 1.9.0
    print("Your numpy version may be out of date")
    print("Please try to update it.")
    import sys
    sys.exit()

def sample(x, size=None, replace=False, prob=None):
    """

    :param x: If an ndarray, a random sample is generated from its elements.
              If an int, the random sample is generated as if x was np.arange(n)
    :param size: int or tuple of ints, optional. Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
                 ``m * n * k`` samples are drawn. Default is None, in which case a single value is returned.
    :param replace: boolean, optional. Whether the sample is with or without replacement
    :param p: 1-D array-like, optional. The probabilities associated with each entry in x.
              If not given the sample assumes a uniform distribution over all entries in x.
    :return: 1-D ndarray, shape (size,). The generated random samples
    """
    if not size:
        size = len(x)
    return np.random.choice(x, size, replace, prob)


def sample_int(n, size=0, replace=False, prob=None):
    """

    :param n: int, the number of items to choose from
    :param size: int, a non-negative integer giving the number of items to choose
    :param replace: bool, Whether the sample is with or without replacement
    :param prob: 1-D array-like, optional. The probabilities associated with each entry in x.
                 If not given the sample assumes a uniform distribution over all entries in x.
    :return:
    """
    if size == 0:
        size = n
    if replace and prob is None:
        return np.random.randint(1, n + 1, size)
    else:
        return sample(range(1, n+1), size, replace, prob)


def matrix(data=np.nan, nrow=1, ncol=1):
    """

    :param data:
    :param nrow:
    :param ncol:
    :return:
    """
    if type(data) == int or type(data) == bool:
        if data == 0 or data == False:
            mat = np.zeros((nrow, ncol))
        elif data == 1 or data == True:
            mat = np.ones((nrow, ncol))
        else:
            print("Unsupported int")
            mat = np.zeros((nrow, ncol))
    else:
        mat = np.matrix(data)
    return mat.reshape(nrow, ncol)


def rep(x, times=1, length_out=np.nan, each=1):
    """
    Replicate Elements of Vectors and Lists
    :param x:
    :param times:
    :param length_out:
    :param each:
    :return:
    """
    if each > 1:
        vec = np.repeat(x, each)
    else:
        if type(x) == int or type(x) == float:
            # import numbers
            # isinstance(n, numbers.Number)
            vec = np.repeat(x, times)
        else:
            vec = x*times
    if length_out is not np.nan:
        return vec[:length_out, ]
    else:
        return vec


def build_subsample_set(X_train, k_n, unique_sample=np.nan, replace=False):
    """
    Build subsample
    :param unique_sample: int, the observation must included in the set
    :param replace: bool, taken with replace or not
    :return: ndarray, indecies of subsamples
    """
    n_train = X_train.shape[0]
    if unique_sample is not np.nan:
        sub_sample_candidate = np.delete(np.arange(n_train), unique_sample)
        sub_sample = sample(sub_sample_candidate, k_n - 1, replace=replace)
        sub_sample = np.append(sub_sample, unique_sample)
    else:
        sub_sample = sample(np.arange(n_train), k_n, replace=replace)

    return sub_sample


def _atom_runner(X_train, Y_train, X_test, k_n, n_MC=200, final_pred=None, reg=False):
    """
    Runner
    :param final_pred:
    :return:
    """
    n_train = X_train.shape[0]
    y_hat = matrix(0, n_MC, X_test.shape[0])

    # Select initial fixed point $\tilde{z}^{(i)}$
    z_i = np.random.randint(0, n_train - 1)

    for j in range(n_MC):
        # Select subsample
        # $S_{\tilde{z}^{(i)},j}$ of size $k_n$ from training set that includes $\tilde{z}^{(i)}$
        sub_sample = build_subsample_set(X_train, k_n, z_i)

        x_ss = X_train[sub_sample, :]
        y_ss = Y_train[sub_sample]

        # Build tree using subsample $S_{\tilde{z}^{(i)},j}$
        if reg:
            tree = RandomForestRegressor(bootstrap=False, n_estimators=1, min_samples_leaf=2)
        else:
            tree = RandomForestClassifier(bootstrap=False, n_estimators=1, min_samples_leaf=2)
        tree.fit(x_ss, y_ss)

        # Use tree to predict at $x^*$
        tmp = tree.predict(X_test)
        '''
        if final_pred is not None and tree.n_classes_ > 2:
            result_p = tmp == final_pred
            result_n = tmp != final_pred
            tmp[result_p] = 1
            tmp[result_n] = 0
        '''
        y_hat[j, :] = tmp
        # self.all_y_hat[i * self.n_MC + j, :] = tmp
    return y_hat


def calculate_variance(X_train, Y_train, X_test, final_pred=None, sub_sample_size=np.nan, n_z_sim=25, n_MC=200, reg=False, covariance=False):
    """
    Internal Variance Estimation Function
    :param X_train:
    :param X_test:
    :param final_pred:
    :param sub_sample_size:
    :param n_z_sim:
    :param n_MC:
    :param reg:
    :param covariance: bool, whether covariance should be returned instead of variance, default is False
    :return: tuple, the first element is the estimation of $\theta_kn$,
            the second element is the estimation of $variance$ or $covariance$
    """
    n = X_train.shape[0]
    if sub_sample_size is np.nan:
        k_n = int(n * 0.3)
    else:
        k_n = sub_sample_size
    mean_y_hat = matrix(0, n_z_sim, X_test.shape[0])
    all_y_hat = matrix(0, n_z_sim * n_MC, X_test.shape[0])

    pool = multiprocessing.Pool(processes=cpu_count())
    rfs = list()

    for i in range(n_z_sim):
        rfs.append(pool.apply_async(_atom_runner, (X_train, Y_train, X_test, k_n, n_MC, final_pred, reg)))
    pool.close()
    pool.join()

    for i, rf in enumerate(rfs):
        y_hat = rf.get()
        for j in range(n_MC):
            all_y_hat[i * n_MC + j, :] = y_hat[j, :]
        # Record average of the $n_{MC}$ predictions
        mean_y_hat[i, :] = np.mean(y_hat, axis=0)

    if reg:
        # Regression
        theta = np.mean(all_y_hat, axis=0)
    else:
        # Classification
        theta = np.zeros(X_test.shape[0])

    for i in range(all_y_hat.shape[1]):
        tmp = np.unique(all_y_hat[:, i], return_counts=True)
        max_index = np.argmax(tmp[1])
        theta[i] = tmp[0][max_index]

    m = n_MC * n_z_sim
    if covariance:
        cov_1_kn = np.cov(mean_y_hat.T)
        cov_kn_kn = np.cov(all_y_hat.T)
        cov_cp1 = ((k_n ** 2) / n) * cov_1_kn
        cov_cp2 = cov_kn_kn / m
        cov_u = cov_cp1 + cov_cp2
        return theta, cov_u
    else:
        var_1_kn = np.var(mean_y_hat, axis=0)
        var_kn_kn = np.var(all_y_hat, axis=0)
        var_cp_1 = ((k_n ** 2) / n) * var_1_kn
        var_cp_2 = var_kn_kn / m
        var_u = var_cp_1 + var_cp_2
        return theta, var_u


if __name__ == "__main__":
    from sklearn.datasets import load_boston
    from sklearn.model_selection import train_test_split
    import sklearn.model_selection as xval
    from sklearn.datasets.mldata import fetch_mldata
    '''
    boston = load_boston()
    Y = boston.data[:, 12]
    X = boston.data[:, 0:12]

    bos_X_train, bos_X_test, bos_y_train, bos_y_test = xval.train_test_split(X, Y, test_size=0.3)
    '''
    mpg_data = fetch_mldata('mpg')

    mpg_X = mpg_data["data"]
    mpg_y = mpg_data["target"]

    mpg_X_train, mpg_X_test, mpg_y_train, mpg_y_test = xval.train_test_split(mpg_X, mpg_y, test_size=0.25, random_state=42)

    v = calculate_variance(mpg_X_train, mpg_y_train, mpg_X_test, reg=True)

    print(v)
