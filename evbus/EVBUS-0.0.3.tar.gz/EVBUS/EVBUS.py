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


class varU(object):
    """
    EVBUS (Estimate Variance Based on U-Statistics)
    Symbols in the code:
    c, selected c observations, which is the initial fixed points.
    k_n, size of subsamples
    n_MC, number of subsamples | number of trees sharing a observation (L)
    m_n, number of subsamples
    n_z_sim, number of initial sets | number of common observations between trees (B)
    ntree = $L * B$
    @Note: In sklearn, the sub-sample size is always the same as the
    original input sample size but the samples are drawn with
    replacement if bootstrap=True (default).
    """
    def __init__(self, X_train, Y_train, X_test, sub_sample_size=np.nan, n_z_sim=25, n_MC=200, regression=True):
        """
        __init__
        :param X_train: ndarray
        :param Y_train: ndarray
        :param X_test: ndarray
        :param sub_sample_size: int, size of sample to draw, default value is 0.632*n for subsamples
        :param n_z_sim: int, number of common observations between trees (B)
        :param n_MC: int, number of trees sharing a observation (L)
        :param regression: bool, True for regression, False for classification
        """
        self.X_train = X_train
        self.Y_train = Y_train
        self.X_test = X_test
        self.n_z_sim = n_z_sim
        self.n_MC = n_MC
        self.n = X_train.shape[0]
        self.reg = regression
        if sub_sample_size is np.nan:
            self.k_n = int(self.n * 0.3)
        else:
            self.k_n = sub_sample_size

    def sample(self, x, size=None, replace=False, prob=None):
        """
        Take a sample of the specified size from the elements of x using either with or without replacement
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

    def sample_int(self, n, size=0, replace=False, prob=None):
        """
        Return an integer vector of length size with elements from 1:n
        :param n: int, the number of items to choose from
        :param size: int, a non-negative integer giving the number of items to choose
        :param replace: bool, Whether the sample is with or without replacement
        :param prob: 1-D array-like, optional. The probabilities associated with each entry in x.
                     If not given the sample assumes a uniform distribution over all entries in x.
        :return: 1-D ndarray, shape (size,). The generated random samples
        """
        if size == 0:
            size = n
        if replace and prob is None:
            return np.random.randint(1, n + 1, size)
        else:
            return self.sample(range(1, n + 1), size, replace, prob)

    def matrix(self, data=np.nan, nrow=1, ncol=1):
        """
        Build matrix like the operation in R
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

    def rep(self, x, times=1, length_out=np.nan, each=1):
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
                vec = np.repeat(x, times)
            else:
                vec = x * times
        if length_out is not np.nan:
            return vec[:length_out, ]
        else:
            return vec

    def build_subsample_set(self, unique_sample=np.nan, replace=False):
        """
        Build subsample
        :param unique_sample: int, the observation must included in the set
        :param replace: bool, taken with replace or not
        :return: ndarray, indecies of subsamples
        """
        n_train = self.X_train.shape[0]
        if unique_sample is not np.nan:
            sub_sample_candidate = np.delete(np.arange(n_train), unique_sample)
            sub_sample = self.sample(sub_sample_candidate, self.k_n - 1, replace=replace)
            sub_sample = np.append(sub_sample, unique_sample)
        else:
            sub_sample = self.sample(np.arange(n_train), self.k_n, replace=replace)

        return sub_sample

    def estimate_zeta_1_kn(self):
        """
        Estimate $\zeta_{1,k_n}$
        :return: 1d array, variance for the test samples
        """
        n_train = self.X_train.shape[0]
        mean_y_hat = self.matrix(0, self.n_z_sim, self.X_test.shape[0])
        for i in range(self.n_z_sim):
            y_hat = self.matrix(0, self.n_MC, self.X_test.shape[0])

            # Select initial fixed point $\tilde{z}^{(i)}$
            z_i = np.random.randint(0, n_train-1)

            for j in range(self.n_MC):
                # Select subsample
                # $S_{\tilde{z}^{(i)},j}$ of size $k_n$ from training set that includes $\tilde{z}^{(i)}$
                sub_sample = self.build_subsample_set(z_i)

                x_ss = self.X_train[sub_sample, :]
                y_ss = self.Y_train[sub_sample]

                # Build tree using subsample $S_{\tilde{z}^{(i)},j}$
                if self.reg:
                    tree = RandomForestRegressor(bootstrap=False, n_estimators=1, min_samples_leaf=2)
                else:
                    tree = RandomForestClassifier(bootstrap=False, n_estimators=1, min_samples_leaf=2)
                tree.fit(x_ss, y_ss)

                # Use tree to predict at $x^*$
                y_hat[j, :] = tree.predict(self.X_test)

            # Record average of the $n_{MC}$ predictions
            mean_y_hat[i, :] = np.mean(y_hat, axis=0)

        # Compute the variance of the $n_{\tilde{z}}$ averages
        var_1_kn = np.var(mean_y_hat, axis=0)

        return var_1_kn

    def estimate_zeta_kn_kn(self):
        """
        Estimate $\zeta_{{k_n},{k_n}}$
        :return:
        """
        y_hat = self.matrix(0, self.n_z_sim, self.X_test.shape[0])
        for i in range(self.n_z_sim):
            # select sample of size $k_n$ from training set
            sub_sample = self.build_subsample_set()

            x_ss = self.X_train[sub_sample, :]
            y_ss = self.Y_train[sub_sample]

            # Build tree using subsample $S_{\tilde{z}^{(i)},j}$
            if self.reg:
                tree = RandomForestRegressor(bootstrap=False, n_estimators=1, min_samples_leaf=2)
            else:
                tree = RandomForestClassifier(bootstrap=False, n_estimators=1, min_samples_leaf=2)
            tree.fit(x_ss, y_ss)

            # Use tree to predict at $x^*$
            y_hat[i, :] = tree.predict(self.X_test)

        # Compute the variance of the $n_{\tilde{z}} predictions$
        var_kn_kn = np.var(y_hat, axis=0)
        return var_kn_kn

    def calculate_variance(self, covariance=False):
        """
        Internal Variance Estimation Method
        :param covariance: bool, whether covariance should be returned instead of variance, default is False
        :return: tuple, the first element is the estimation of $\theta_kn$,
                        the second element is the estimation of $variance$ or $covariance$
        """
        n_train = self.X_train.shape[0]
        mean_y_hat = self.matrix(0, self.n_z_sim, self.X_test.shape[0])
        all_y_hat = self.matrix(0, self.n_z_sim*self.n_MC, self.X_test.shape[0])
        for i in range(self.n_z_sim):
            y_hat = self.matrix(0, self.n_MC, self.X_test.shape[0])

            # Select initial fixed point $\tilde{z}^{(i)}$
            z_i = np.random.randint(0, n_train - 1)

            for j in range(self.n_MC):
                # Select subsample
                # $S_{\tilde{z}^{(i)},j}$ of size $k_n$ from training set that includes $\tilde{z}^{(i)}$
                sub_sample = self.build_subsample_set(z_i)

                x_ss = self.X_train[sub_sample, :]
                y_ss = self.Y_train[sub_sample]

                # Build tree using subsample $S_{\tilde{z}^{(i)},j}$
                if self.reg:
                    tree = RandomForestRegressor(bootstrap=False, n_estimators=1, min_samples_leaf=2)
                else:
                    tree = RandomForestClassifier(bootstrap=False, n_estimators=1, min_samples_leaf=2)
                tree.fit(x_ss, y_ss)

                # Use tree to predict at $x^*$
                tmp = tree.predict(self.X_test)
                y_hat[j, :] = tmp
                all_y_hat[i*self.n_MC+j, :] = tmp
            # Record average of the $n_{MC}$ predictions
            mean_y_hat[i, :] = np.mean(y_hat, axis=0)

        if self.reg:
            # Regression
            theta = np.mean(all_y_hat, axis=0)
        else:
            # Classification
            theta = np.zeros(self.X_test.shape[0])

            for i in range(all_y_hat.shape[1]):
                tmp = np.unique(all_y_hat[:, i], return_counts=True)
                max_index = np.argmax(tmp[1])
                theta[i] = tmp[0][max_index]
        
        # Compute the variance of the $n_{\tilde{z}}$ averages
        m = self.n_MC * self.n_z_sim
        # m = self.n_MC
        alpha = self.n / m
        """
        $variance = \frac{1}{\alpha}\frac{k^2}{m}\zeta_{1,k}+\frac{1}{m}\zeta_{k,k}$
        $\alpha = \frac{n}{m}$
        $variance = \frac{k^2}{n}\zeta_{1,k}+\frac{1}{m}\zeta_{k,k}$
        """
        if covariance:
            cov_1_kn = np.cov(mean_y_hat.T)
            cov_kn_kn = np.cov(all_y_hat.T)
            cov_cp1 = ((self.k_n**2) / self.n) * cov_1_kn
            cov_cp2 = cov_kn_kn / m
            cov_u = cov_cp1 + cov_cp2
            return theta, cov_u
        else:
            var_1_kn = np.var(mean_y_hat, axis=0)
            var_kn_kn = np.var(all_y_hat, axis=0)
            var_cp_1 = ((self.k_n**2) / self.n) * var_1_kn
            var_cp_2 = var_kn_kn / m
            var_u = var_cp_1 + var_cp_2
            return theta, var_u
