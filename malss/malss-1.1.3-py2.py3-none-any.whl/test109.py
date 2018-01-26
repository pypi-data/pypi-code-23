# coding: utf-8

from sklearn.datasets import load_iris
from malss import MALSS

if __name__ == '__main__':
    iris = load_iris()
    clf = MALSS('classification')
    clf.fit(iris.data, iris.target, algorithm_selection_only=True)
    # for i in range(5):
    #     clf.remove_algorithm(0)
    clf.fit(iris.data, iris.target, 'report')
