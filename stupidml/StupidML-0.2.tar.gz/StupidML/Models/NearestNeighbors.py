import numpy as np
from sklearn.utils.extmath import safe_sparse_dot as safedot
from ..Utilities.utils import Kernel

# import os
# print(os.getcwd())
# import sys
# sys.exit(1)

class NearestNeighbors():
    def l1_distance(self, X, x):
        raw_dist = np.abs(X - x)
        return np.sum(raw_dist, axis = 1)


    def l2_distance(self, X, x, gen_dist, kernel, **kwargs):
        if kernel is None:
            t_1 = gen_dist
            t_2 = safedot(x, x)
            t_3 = 2 * safedot(X, x)
            return t_1 + t_2 - t_3
        else:
            distances = np.zeros(X.shape[0])
            for i in range(X.shape[0]):
                t_2 = kernel(x, x, **kwargs)
                t_3 = kernel(X[i], x, **kwargs)
                distances[i] = gen_dist[i] + t_2 - (2 * t_3)
            return distances


    def lp_distance(self, X, x, p = 3):
        abs_dist = np.abs(X - x)
        nth_dist = np.sum(np.power(abs_dist, p), axis = 1)
        distances = np.power(nth_dist, (1 / p))
        return distances


    def min_distances(self, distances, y, k):
        while k > 0:
            min_distances = np.argpartition(distances, k)[:k]
            labels = y[min_distances]
            prediction = np.median(labels)
            if prediction.is_integer() or k == 1:
                return prediction
            else:
                k -= 1
        return prediction


    def classify(self, X_train, y_train, X_test, k = 3, dist_func = "l2", p = 3, kernel = None, **kwargs):
        func_map = {'l1': self.l1_distance, 'l2': self.l2_distance, 'lp' : self.lp_distance}

        kern = Kernel()
        kernel_map = {'rbf': kern.gaussian, 'polynomial' : kern.polynomial, 'sigmoid' : kern.sigmoid}

        if dist_func == 'l2':
            gen_dist = np.sum(X_train * X_train, axis = 1)

        if kernel:
            gen_dist = np.zeros(X_train.shape[0])
            for i in range(X_train.shape[0]):
                gen_dist[i] = kernel_map[kernel](X_train[i], X_train[i], **kwargs)

        pred = np.zeros(X_test.shape[0])
        for i in range(X_test.shape[0]):
            if dist_func == 'l2':
                if kernel == None:
                    distances = func_map[dist_func](X_train, X_test[i], gen_dist, kernel)

                else:
                    distances = func_map[dist_func](X_train, X_test[i], gen_dist, kernel_map[kernel] , **kwargs)

            elif dist_func == 'lp':
                distances = func_map[dist_func](X_train, X_test[i], p = p)

            else :
                distances = func_map[dist_func](X_train, X_test[i])

            pred[i] = self.min_distances(distances, y_train, k)
        return pred


