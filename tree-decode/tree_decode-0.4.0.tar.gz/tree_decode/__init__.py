from .api import *  # noqa

__version__ = "0.4.0"

__doc__ = """
tree_decode - Library that helps to remove the black-box
surrounding decision trees from scikit-learn, making it
easier to understand how they work and more importantly,
to diagnose their issues when they produce unexpected results.

The decision tree classes that scikit-learn currently supports are:

* DecisionTreeClassifier
* DecisionTreeRegressor
* ExtraTreeClassifier
* ExtraTreeRegressor

* RandomForestClassifier
* RandomForestRegressor
* ExtraTreesClassifier
* ExtraTreesRegressor
"""


def demo():
    """
    Execute the demo for `tree_decode` that shows all of the functionality.
    """

    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.datasets import load_iris

    iris = load_iris()
    y = iris.target
    x = iris.data

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)
    estimator = DecisionTreeClassifier(max_leaf_nodes=3, random_state=0)

    estimator.fit(x_train, y_train)
    print(get_tree_info(estimator))  # noqa

    names = {0: "Sepal Length", 1: "Sepal Width",
             2: "Petal Length", 3: "Petal Width"}
    print(get_tree_info(estimator, names=names))  # noqa

    print(get_tree_info(estimator, precision=None))  # noqa
    print(get_tree_info(estimator, normalize=False))  # noqa
    print(get_tree_info(estimator, label_index=2))  # noqa
    print(get_tree_info(estimator, tab_size=2))  # noqa

    index = 1
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")
    print(get_decision_info(estimator, data))  # noqa

    index = 2
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")
    print(get_decision_info(estimator, data, precision=None))  # noqa

    index = 3
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")
    print(get_decision_info(estimator, data, names=names))  # noqa
    print(get_decision_info(estimator, data, label_index=2))  # noqa
    print(get_decision_info(estimator, data, tab_size=2))  # noqa


def test():
    """
    Run unit tests on the current tree_decode installation.
    """

    try:
        import pytest  # noqa
    except ImportError:
        raise ImportError("pytest not found. Please install "
                          "with `pip install pytest`")

    from subprocess import call
    from os.path import dirname

    directory = dirname(__file__)
    call(["pytest", directory])
