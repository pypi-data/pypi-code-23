import numpy as np
import numpy.linalg as la
from sklearn.utils.extmath import safe_sparse_dot as safedot

class DiscriminantAnalysis():

    def __init__(self, model = 'Linear'):
        if model not in ['Linear', 'Quadratic', 'Regularized']:
            raise ValueError('Invalid model name')
        self.model = model


    def compute_priors(self, y):
        priors = np.empty(shape = (len(np.unique(y))))

        for i in range(len(priors)):
            priors[i] = np.sum(y == (i))

        priors_ = priors / len(y)
        self.priors = priors_

    def compute_means(self, X, y):
		means = np.empty(shape = (len(np.unique(y)), len(X[0])))
        for i in range(len(means)):
            means[i] = np.mean(X[y == i], axis = 0)
        self.means = means

    def compute_covariance(self, X, y):
        d1 = len(self.means)
        d2 = len(self.means[0])

        c_var = np.empty(shape = (d1,d2,d2))

        for i in range(len(c_var)):
            c_var[i] = np.cov(X[y == i].T)
        self.Sigma = c_var


    def pool_sigma(self, y):
        cov_mat = np.zeros(shape = self.Sigma[0].shape)
        for i in range(len(self.means)):
            cov_mat += (np.sum(y == i) * self.Sigma[i])
        cov_mat = cov_mat / (len(y) - len(self.means))
        self.pooled_sigma = cov_mat

    def regularize_covariance(self, reg):
        for i in range(self.Sigma.shape[0]):
            self.Sigma[i] = (reg * self.Sigma[i]) + (1 - reg) * self.pooled_sigma

    def create_variables(self, X):
        try:
            inv_sigma = la.inv(self.pooled_sigma)
        except:
            inv_sigma = la.pinv(self.pooled_sigma)

        self.gamma = np.zeros(shape = self.priors.shape[0])
        self.beta = np.zeros(shape = (self.gamma.shape[0], X.shape[1]))

        for i in range(self.priors.shape[0]):
            a = safedot(self.means[i], inv_sigma)
            b = safedot(a, self.means[i]) / (-2)
            self.gamma[i] = b + np.log(self.priors[i])
            self.beta[i] = safedot(inv_sigma, self.means[i])


    def decompose(self, i):
        w, U = la.eig(self.Sigma[i])
        w += np.mean(np.nonzero(w)) # if there is a zero along the diagonal, matrix will be singular, so
        # a value must be added to make the matrix D invertible
        D = np.diag(w)
        return D,U

    def get_decomposition(self):
        d1 = len(self.Sigma)
        d2 = len(self.Sigma[0])
        D = np.empty(shape = (d1, d2, d2))
        U = np.empty(shape = (d1, d2, d2))
        for i in range(d1):
            D[i], U[i] = self.decompose(i)
        self.D = D
        self.U = U
        self.D_i = la.inv(D)

    def compute_determinant(self):
        self.determinants = np.zeros(self.priors.shape[0])
        for i in range(self.Sigma.shape[0]):
            self.determinants[i] = np.sum(np.log(np.diag(self.D[i])))

    def compute_mahalanobis(self, X):
        length = self.means.shape[0]
        t_0 = np.zeros(shape = (length, X.shape[0], X.shape[1]))
        for i in range(length):
            t_0[i] = np.dot(X - self.means[i], self.U[i].T)

        mahalanobis = np.zeros(shape = (length, X.shape[0]))
        for i in range(length):
            l = np.dot(t_0[i], self.D_i[i])
            mahalanobis[i] = np.sum(l * t_0[i], axis = 1)
        return mahalanobis.T


    def softmax(self, n):
        e_n = np.exp(n - np.max(n))
        return e_n / np.sum(e_n)


    def fit(self,X, y, reg = 1):
        if (type(X) != np.ndarray):
            raise ValueError("Data must be formatted in numpy array")

        self.compute_priors(y)
        self.compute_means(X, y)
        self.compute_covariance(X, y)

        if (self.model == 'Linear'):
            self.pool_sigma(y)
            self.create_variables(X)

        elif (self.model == 'Quadratic'):
            self.get_decomposition()
            self.compute_determinant()

        elif (self.model == 'Regularized'):
            self.pool_sigma(y)
            self.regularize_covariance(reg)
            self.get_decomposition()
            self.compute_determinant()


    def classify(self, X):
		if (self.model == 'Linear'):
            n = safedot(X, self.beta.T) + self.gamma
            self.predictions = np.argmax(self.softmax(n), axis = 1)

        elif (self.model == 'Quadratic' or self.model == 'Regularized'):
            t_1 = (-0.5) * self.determinants
            t_2 = (-0.5) * self.compute_mahalanobis(X)
            self.predictions = np.argmax(t_1 + t_2 , axis = 1)
