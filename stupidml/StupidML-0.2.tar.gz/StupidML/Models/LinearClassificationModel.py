import numpy as np
import numpy.linalg as la
from sklearn.utils.extmath import safe_sparse_dot as safedot
from scipy.special import expit
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics

class LinearClassificationModel():

    def __init__(self, binary = False):
        self.binary = binary


    def step_size(self, iter_num, k = 0.5, t = 100):
        return ((t + iter_num) ** (-k))


    def threshold(self, y, threshold):
        y[y >= threshold] = 1
        y[y < threshold] = 0
        return y


    def convert_labels_binary(self,X, w, threshold = 0.5):
        n_pred = expit(safedot(X, w))
        y = self.threshold(n_pred, threshold)
        return y


    def score_irls(self, y, pi, S):
        error = safedot(la.pinv(S),(y - pi))
        return error


    def irls(self, X, y, iterations = 50, l2_reg = 0, save_weights = False):
        w = np.zeros(X.shape[1])
        prediction = np.ones(X.shape[1])
        if save_weights:
            W = np.empty(shape = ((iterations), w.shape[0]))
        i = 0
        while i < iterations:
            n = safedot(X,w)
            prediction = expit(n) # predicting new y values based on current weights
            s = prediction * (1 - prediction)
            s[s == 0] = np.finfo('float').resolution # Ensuring that matrix S will be invertible
            S = np.diag(s)

            z = n + self.score_irls(y, prediction, S) # response variable
            if np.allclose(z, n):
                if (save_weights):
                    W = W[:i]
                break
            w_0 = la.inv(la.multi_dot((X.T,S, X)))
            w_1 = la.multi_dot((X.T, S, z))

            w_n = safedot(w_0, w_1)
            w = w_n + (l2_reg * w)
            if save_weights:
                W[i] = w
            i += 1
        self.w = w
        if save_weights:
            self.W = W


    def init_bfgs(self, X, y):
        W = np.zeros(shape = (2, X.shape[1])) # initializing weights 
        B = np.zeros(shape = (2, X.shape[1], X.shape[1]))

        B[0] = np.diag(np.ones(shape=X.shape[1])) # Initializing pseudo-hessian to identity matrix
        pi = expit(safedot(X, W[0]))

        G = np.empty(shape = (2, X.shape[1]))
        G[0] = safedot(X.T,(pi - y))
        return W, B, G


    def update_B(self, B, W, G):
        dW = W[1] - W[0]
        dG = G[1] - G[0]
        t_1a = safedot(dG, dG)
        t_1b = safedot(dG, dW)
        if not t_1b:
            t_1 = 0
        else: 
            t_1 = t_1a / t_1b
        t_2a = safedot(safedot(B[0], dW), safedot(B[0], dW))
        t_2b = safedot(safedot(dW, B[0]),dW)
        B[1] = B[0] + t_1 + (t_2a / t_2b)
        return B[1]


    def bfgs(self, X, y, iterations = 20, save_weights = False, t = 0,  k = .12):

        W, B, G = self.init_bfgs(X,y)
        weights = np.empty(shape = (iterations, W.shape[1]))

        for i in range(iterations):     
            n = safedot(X,W[0])
            G[1] = (safedot(X.T, expit(n) - y)  ) / G.shape[1]
            d = safedot(la.pinv(B[0]), G[1])

            a = self.step_size(iter_num = (i + 1) * 10 , t = t, k = k)

            W[1] = W[0] - (a * d)
        
            B[0] = self.update_B(B, W, G)
            
            G[0] = G[1]
            W[0] = W[1]

            if save_weights:
                weights[i] = W[0]
            
        self.w = W[0] 
        if save_weights:
            self.W = weights


    def get_batch(self, X, y, iteration, size):
        max_idx = iteration * size % X.shape[0]
        min_idx = max_idx - size % X.shape[0]
        if max_idx < size:
            batch = np.concatenate((X[min_idx:], X[:max_idx]))
            labels = np.concatenate((y[min_idx:], y[:max_idx]))
        else:
            batch = X[min_idx:max_idx]
            labels = y[min_idx: max_idx]
        return batch, labels


    def batch_sgd(self, X, y, epsilon, max_iters = 100, size = 100, save_weights = False):
        w = w_0 = np.zeros(X.shape[1])
        if save_weights:
            W = np.zeros(shape=(max_iters, X.shape[1]))
        i = 0
        while i < max_iters:
            batch_x, batch_y = self.get_batch(X, y, i, size)
            pi = expit(np.dot(batch_x, w))
            gradient = np.dot(batch_x.T,(pi - batch_y))
            alpha = self.step_size((i + 1) * size)
            
            w = w_0 - (alpha * gradient)
            if save_weights:
                W[i] = w

            if la.norm(w_0 - w) < epsilon:
                if save_weights:
                    W = W[:i]
                break
            w_0 = w
            i += 1
        if save_weights:
            self.W = W
        self.w = w


    def conjugate_gradient(self, A, b, epsilon, x = None):
		if x is None:
            x = np.ones(b.shape[0]) # Initialize random x
        r_0 = safedot(A, x) - b # Calculating residual 
        p = - r_0 # original direction

        while la.norm(r_0) > epsilon:
            alpha = safedot(r_0,r_0) / safedot(safedot(p,A),p) # Creating 1-D minimizer

            x = x + (alpha * p) # Updating x
            r_1 = r_0 + (alpha * safedot(A, p)) # Updating residual
            beta = safedot(r_1, r_1) / safedot(r_0,r_0) # matrix to ensure conjugacy between new direct p and A

            p = -r_1 + safedot(beta, p) # updating direction
            r_0 = r_1
        return x


    def binary_newton_cg(self, X, y, max_iters = 10, l2_reg = 0, save_weights = False, epsilon = 1e-4):
		w = np.zeros(X.shape[1])
        if save_weights:
            W = np.zeros(shape=(max_iters, X.shape[1]))
        for i in range(max_iters):

            mu = expit(safedot(X,w)) # Calculating predicted probabilities

            g = safedot(X.T,(mu - y)) # gradient vector
            H = safedot(safedot(X.T, np.diag(mu)),X) # hessian matrix

            n = self.conjugate_gradient(H, g, epsilon) # 

            w = (w - n) + (l2_reg * w) # updating weights with l2 regularization 
            if save_weights:
                W[i] = w
        if save_weights:
            self.W = W # weights of each iteration
        self.w = w # final weights


    def binary_classify(self, X):
        self.predictions = self.convert_labels_binary(X, self.w)


    def fit(self, X, y, solver = 'newton_cg', max_iters = 10, l2_reg = 0.5, save_weights = False, convergence_param = 1e-4):
        if solver not in ['newton_cg', 'batch_sgd', 'perceptron', 'irls', 'bfgs']:
            raise Exception("Must choose proper solver")

        if (np.unique(y).shape[0]) > 2:
            self.binary = False
            if solver not in ['newton_cg', 'batch_sgd']:
                raise Exception("Must use proper solver for multi-class data")
            else:
                self.model = 'Multi-Class'
                self.solver = solver
                pass
        else: 
            self.binary = True;

            self.model = 'Binary'
            self.solver = solver

            if (solver == 'newton_cg'):
                self.binary_newton_cg(X, y, max_iters, l2_reg, save_weights = save_weights, epsilon = convergence_param)

            elif (solver == 'batch_sgd'):
                self.batch_sgd(X, y, save_weights = save_weights, max_iters = max_iters, epsilon = convergence_param)

            elif (solver == 'irls'):
                self.irls(X, y, max_iters, l2_reg = l2_reg, save_weights = save_weights)

            elif (solver == 'bfgs'):
               self.bfgs(X, y, iterations = max_iters, save_weights = save_weights)


    def classify(self, X):
        if self.binary:
            self.binary_classify(X)


class Perceptron():
    def fit(self, X, y, max_iters = 10000, save_weights = False, epsilon = 1e-5):
        if not np.allclose(np.unique(y), np.array([-1,1])):
            y[y == 0] = -1

        w = - np.ones(shape=X.shape[1]) + np.finfo('float').resolution
        W = np.zeros(shape = (max_iters, w.shape[0]))
        s = np.zeros(w.shape[0])
        for i in range(max_iters):
            idx = i % (X.shape[0] -1)
            x = X[idx]
            y_hat = np.sign(safedot(x, w))

            # Only updates when an incorrect predict is made
            if not np.allclose(y_hat, y[idx]):
                w += y[idx] * x
            
            W[i] = w
            if i > 50 and la.norm(W[i] - W[i - 50]) < epsilon:
                break
        self.w = w
        self.W = W


    def classify(self, X):
        preds = np.sign(safedot(X,self.w))
        preds[preds < 1] = 0
        self.predictions = preds


class VisualizeLinearModel():

    def __init__(self, style = 'seaborn-darkgrid'):
        plt.style.use(style)
        sns.set()


    def prepare_visualization(self, model, X_test, y_test, X_train, y_train):
        size = model.W.shape[0];
        train_accuracy = np.zeros(shape=(size))
        test_accuracy = np.zeros(shape= train_accuracy.shape)

        confusion_matrix_test = np.zeros(shape = (size, 2, 2))
        confusion_matrix_train = np.zeros(shape = (size, 2, 2))

        for i in range(size):
            train_predictions = model.convert_labels_binary(X_train, model.W[i])
            test_predictions = model.convert_labels_binary(X_test, model.W[i])
            train_accuracy[i] = np.sum(train_predictions == y_train) / y_train.shape[0]
            test_accuracy[i] = np.sum(test_predictions == y_test) / y_test.shape[0]
            confusion_matrix_train[i] = metrics.confusion_matrix(y_train, train_predictions)
            confusion_matrix_test[i] = metrics.confusion_matrix(y_test, test_predictions)

        self.train_accuracy = train_accuracy
        self.test_accuracy = test_accuracy

        self.train_TN = confusion_matrix_train[:,0,0] / np.sum(y_train == 0)
        self.train_FN = confusion_matrix_train[:,1,0] / np.sum(y_train == 0)
        self.train_TP = confusion_matrix_train[:,1,1] / np.sum(y_train == 1)
        self.train_FP = confusion_matrix_train[:,0,1] / np.sum(y_train == 1)

        self.test_TN = confusion_matrix_test[:,0,0] / np.sum(y_test == 0)
        self.test_FN = confusion_matrix_test[:,1,0] / np.sum(y_test == 0)
        self.test_TP = confusion_matrix_test[:,1,1] / np.sum(y_test == 1)
        self.test_FP = confusion_matrix_test[:,0,1] / np.sum(y_test == 1)


    def show_visualization(self, line_size):
        fig1, (ax1, ax2) = plt.subplots(nrows = 2, figsize = (9, 7))

        ax1.set_title("Training Results")
        ax1.plot(self.train_TN, linewidth = line_size, alpha = 0.7, label = "True Negative")
        ax1.plot(self.train_FN, linewidth = line_size, alpha = 0.7, label = "False Negative")
        ax1.plot(self.train_TP, linewidth = line_size, alpha = 0.7, label = "True Positive")
        ax1.plot(self.train_FP, linewidth = line_size, alpha = 0.7, label = "False Positive")
        ax1.legend(frameon=True, loc=5, ncol=1)

        ax2.set_title("Testing Results")
        ax2.plot(self.test_TN, linewidth = line_size, alpha = 0.7, label = "True Negative")
        ax2.plot(self.test_FN, linewidth = line_size, alpha = 0.7, label = "False Negative")
        ax2.plot(self.test_TP, linewidth = line_size, alpha = 0.7, label = "True Positive")
        ax2.plot(self.test_FP, linewidth = line_size, alpha = 0.7, label = "False Positive")
        ax2.legend(frameon=True, loc=5 , ncol=1)

        fig2, ax3 = plt.subplots()
        ax3.set_title("Error Rates")
        ax3.plot(1 - self.train_accuracy, linewidth = line_size, alpha = 0.8,  label = "Training Error")
        ax3.plot(1 -self.test_accuracy, linewidth = line_size, alpha = 0.8, label = "Testing Error")
        ax3.legend(frameon=True, ncol=2);
        plt.show()


    def visualize(self, model, X_test, y_test, X_train, y_train, line_size = 1):
        self.prepare_visualization(model, X_test, y_test, X_train, y_train)
        self.show_visualization(line_size)

