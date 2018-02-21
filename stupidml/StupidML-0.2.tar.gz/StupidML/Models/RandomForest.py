import numpy as np
from DecisionTree import ClassificationTree, RegressionTree
from abc import ABCMeta
from scipy.stats import mode

class RandomForest(metaclass=ABCMeta):
    def __init__(self, num_trees, seed, max_depth, cost_func, min_size, sample_percentage):
        self.num_trees = num_trees
        self.max_depth = max_depth
        self.cost_func = cost_func
        self.min_size = min_size
        self.sample_percentage = sample_percentage
        np.random.seed(seed)

    def fit(self, X, y):
        data = np.column_stack((X, y))
        self.forest = np.empty(shape=self.num_trees, dtype='object')
        sample_size = int(X.shape[0] * self.sample_percentage)

        for i in range(self.num_trees):
            sample = data[np.random.choice(data.shape[0], sample_size, replace=True)]

            sampled_X = data[:, :data.shape[1] - 1]
            sampled_y = data[:, data.shape[1] - 1]

            if isinstance(self, RegressionForest):
                tree = RegressionTree(
                    max_depth=self.max_depth,
                    min_size=self.min_size,
                    in_forest=True)
            else:
                tree = ClassificationTree(
                    cost_func=self.cost_func,
                    max_depth=self.max_depth,
                    min_size=self.min_size,
                    in_forest=True)

            tree.fit(sampled_X, sampled_y)
            self.forest[i] = tree

    def predict(self, X):
        votes = np.zeros(shape=(self.num_trees, X.shape[0]))
        for i, tree in enumerate(self.forest):
            votes[i] = tree.predict(X)

        predictions = np.zeros(shape=X.shape[0])
        if isinstance(self, RegressionForest):
            predictions = votes.mean(axis=0)
        else:
            # print(votes)
            predictions = np.squeeze(mode(votes, axis=0)[0])

        return predictions


class RegressionForest(RandomForest):
    def __init__(self, num_trees=10, seed=0, max_depth=None, min_size=1, sample_percentage=1):
        self.num_trees = num_trees
        self.cost_func = 'mse'
        self.max_depth = max_depth
        self.min_size = min_size
        self.sample_percentage = sample_percentage
        super().__init__(
            num_trees=num_trees,
            seed=seed,
            max_depth=max_depth,
            cost_func=self.cost_func,
            min_size=min_size,
            sample_percentage=sample_percentage
            )


class ClassificationForest(RandomForest):
    def __init__(self, num_trees=10, seed=0, max_depth=None, cost_func='mcr', min_size=1, sample_percentage=1):
        self.num_trees = num_trees
        self.cost_func = cost_func
        self.max_depth = max_depth
        self.min_size = min_size
        self.sample_percentage = sample_percentage
        super().__init__(
            num_trees=num_trees,
            seed=seed,
            max_depth=max_depth,
            cost_func=cost_func,
            min_size=min_size,
            sample_percentage=sample_percentage
            )
