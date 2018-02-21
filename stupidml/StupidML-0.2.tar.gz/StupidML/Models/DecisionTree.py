import numpy as np
import numpy.linalg as la
from abc import ABCMeta
import scipy.stats as stats

class DecisionTree(metaclass=ABCMeta):
    def __init__(self, cost_func, max_depth, min_size, min_impurity, min_cost, in_forest):
        if isinstance(self, RegressionTree):
            self.cost_func = self.regression_cost
        else:
            if cost_func == 'mcr':
                self.cost_func = self.misclassification_rate_cost
            elif cost_func == 'entropy':
                self.cost_func = self.entropy
            elif cost_func == 'gini':
                self.cost_func = self.gini
            else:
                raise ValueError("Must select an appropriate cost function")

        self.max_depth = max_depth
        self.min_size = min_size
        self.min_impurity = min_impurity
        self.min_cost = min_cost
        self.in_forest = in_forest

    def regression_cost(self, y):
        if (y.size == 0):
            return 0
        y_hat = np.mean(y)
        diff = y - y_hat
        return np.square(diff).sum()

    def misclassification_rate_cost(self, y):
        prediction = 0
        for label in np.unique(y):
            cur = np.sum(y == label) / y.shape[0]
            if cur > prediction:
                prediction = cur
        return 1 - prediction

    def entropy(self, y):
        dist = np.empty(np.unique(y).shape)
        for label in range(dist.shape[0]):
            dist[label] = np.sum(y == label) / y.shape[0]
        dist += np.finfo('float').resolution
        return -np.sum(dist * np.log(dist))

    def gini(self, y):
		dist = np.empty(np.unique(y).shape)
        for label in range(dist.shape[0]):
            dist[label] = np.sum(y == label) / y.shape[0]
        return 1 - np.sum(np.square(dist))


    def split(self, X, y, node):
        split_threshold = None
        split_feature = None
        min_response = None

        possible_samples = range(X.shape[1])
        if (self.in_forest):

            if isinstance(self, RegressionTree):
                sample_features = np.random.choice(possible_samples, size = int(X.shape[1] / 3))
            else:
                sample_features = np.random.choice(possible_samples, size = int(np.sqrt(X.shape[1])))
        else:
            sample_features = possible_samples

        for feature in sample_features:
            for thresh in np.unique(X[:, feature]):
                left = y[X[:, feature] <= thresh]
                right = y[X[:, feature] > thresh]
                response = self.cost_func(left) + self.cost_func(right)
                if (min_response is None or response < min_response):
                    split_threshold = thresh
                    split_feature = feature
                    min_response = response

        node.threshold = split_threshold
        node.feature = split_feature
        lower_mask = X[:, split_feature] <= split_threshold
        upper_mask = X[:, split_feature] > split_threshold
        return (X[lower_mask], y[lower_mask]), (X[upper_mask], y[upper_mask])

    def not_worth_splitting(self, data_left, data_right, depth):
        if self.max_depth and depth > self.max_depth:
            return True
        if not isinstance(self, ClassificationTree) and self.cost_reduction(data_left, data_right) < self.min_cost:
            return True
        if data_left[0].size < self.min_size or data_right[0].size < self.min_size:
            return True

        return False

    def cost_reduction(self, data_left, data_right):
        y_total = np.hstack((data_left[1], data_right[1]))
        total_norm = la.norm(y_total)
        left_norm = la.norm(data_left[1])
        right_norm = la.norm(data_right[1])

        total_cost = self.cost_func(y_total)
        normalized_left = (left_norm / total_norm) * self.cost_func(data_left[1])
        normalized_right = (right_norm / total_norm) * self.cost_func(data_right[1])

        return total_cost - (normalized_left + normalized_right)

    def test_purity(self, y):
        common = stats.mode(y)[0][0]
        return np.sum(y == common) == y.size

    def grow_tree(self, node, X, y, depth):
        if isinstance(self, RegressionTree):
            node.mean_dist = np.mean(y)

        else:
            node.mean_dist = common = stats.mode(y)[0][0]
        if y.size < 2:
            return node
        if isinstance(self, ClassificationTree) and self.test_purity(y):
            return node

        data_left, data_right = self.split(X, y, node)

        if self.not_worth_splitting(data_left, data_right, depth):
            return node

        left = DecisionNode()
        right = DecisionNode()
        node.left = self.grow_tree(left, data_left[0], data_left[1], depth + 1)
        node.right = self.grow_tree(right, data_right[0], data_right[1], depth + 1)

        return node

    def single_prediction(self, x, node):
        if x[node.feature] is None or (not node.left and not node.right):
            return node.mean_dist

        go_left = x[node.feature] <= node.threshold

        if (go_left and node.left):
            return self.single_prediction(x, node.left)
        if (not go_left and node.right):
            return self.single_prediction(x, node.right)
        return node.mean_dist

    def fit(self, X, y):
        node = DecisionNode()
        self.root = self.grow_tree(node, X, y, 0)

    def predict(self, X):
        predictions = np.zeros(X.shape[0])
        for i, observation in enumerate(X):
            predictions[i] = self.single_prediction(observation, self.root)
        return predictions


class RegressionTree(DecisionTree):
    def __init__(self, max_depth=None, min_size=5, min_cost=0, in_forest=False):
        self.cost = 'mse'
        self.max_depth = max_depth
        self.min_size = min_size
        self.min_cost = min_cost
        self.in_forest = in_forest
        super().__init__(
            cost_func=self.cost,
            max_depth=self.max_depth,
            min_size=self.min_size,
            min_impurity=None,
            min_cost=self.min_cost,
            in_forest=self.in_forest)


class ClassificationTree(DecisionTree):
    def __init__(self, cost_func='mcr', max_depth=None, min_size=1, min_cost=0, in_forest=False):
        self.cost = cost_func
        self.max_depth = max_depth
        self.min_size = min_size
        self.min_cost = min_cost
        self.in_forest = in_forest
        super().__init__(
            cost_func=self.cost,
            max_depth=self.max_depth,
            min_size=self.min_size,
            min_impurity=None,
            min_cost=self.min_cost,
            in_forest=self.in_forest)


class DecisionNode():
    def __init__(self, threshold=None, mean_dist=None, feature=None):
		self.threshold = threshold
        self.mean_dist = mean_dist
        self.feature = feature
        self.right = None
        self.left = None
