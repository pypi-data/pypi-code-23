import numpy as np
import numpy.linalg as la
from sklearn.utils.extmath import safe_sparse_dot as safedot

class NaiveBayes():

    def __init__(self, model):
        if model not in ['Bernoulli', 'Multinomial']:
            raise Exception('Must specify correct model')
        self.model = model


    def compute_priors(self, y):
        self.classes = np.array(np.unique(y), dtype = 'uint16') ## should not be any negative classes
        self.priors = np.zeros(shape=self.classes.shape[0])
        for i in self.classes:
            self.priors[i] = np.sum(y == self.classes[i]) / y.shape[0]


    def get_bernoulli_probabilities(self, X, y):
        p_matrix = np.zeros(shape=(self.classes.shape[0], X.shape[1]))
        for c in self.classes:
            mask = y == c
            elems = X[mask]
            length = np.sum(mask)
            p_matrix[c] = np.sum(elems, axis = 0) / length

        # preventing value errors when calculating log likelihood
        p_matrix[p_matrix == 0] = np.finfo('float').resolution 
        p_matrix[p_matrix == 1] = 1 - np.finfo('float').resolution
        self.p_matrix = p_matrix


    def get_bernoulli_likelihood(self, X):
        log_p = np.log(self.p_matrix)
        log_p_not = np.log(1 - self.p_matrix)

        a = safedot(1 - X, log_p_not.T)
        b = safedot(X, log_p.T)
        self.predictions = np.argmax(np.log(self.priors) + a + b, axis = 1)


    def get_multinomial_probabilities(self, X, y):
        num_class = self.classes.shape[0]
        p_matrix = np.zeros(shape= (num_class, X.shape[1]))
        for i in range(num_class):
            p_matrix[i] = np.squeeze(np.asarray(X[y == i].sum(axis = 0) / np.sum(y == i)))

        # Need log probability for dot product later, so cannot have zeros
        p_matrix[p_matrix == 0] = np.finfo('float').resolution
        self.l_p_matrix = np.log(p_matrix)


    def get_multinomial_likelihood(self, X):
        ll = safedot(X, self.l_p_matrix.T)
        l_prior = np.log(self.priors)
        self.predictions = np.argmax(ll + l_prior, axis = 1)


    def fit(self, X, y):
        self.compute_priors(y)

        if self.model == 'Bernoulli':
            if (np.unique(X).size > 2):
                raise ValueError("Cannot use Bernoulli model for data that is not binary")
            self.get_bernoulli_probabilities(X, y)

        elif self.model == 'Multinomial':
            self.get_multinomial_probabilities(X, y)


    def classify(self, X):
        if self.model == 'Bernoulli':

            self.get_bernoulli_likelihood(X)
        elif self.model == 'Multinomial':
            self.get_multinomial_likelihood(X)

