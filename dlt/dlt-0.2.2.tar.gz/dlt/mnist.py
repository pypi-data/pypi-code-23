"""
Module to load the MNIST database of handwritten digits
See http://yann.lecun.com/exdb/mnist/

The images are 28x28 pixels (grayscale) showing a single handwritten digit from
0 to 9. The dataset contains 60000 training and 10000 test images.
"""

import numpy as np
from keras.datasets import mnist

from dlt.utils import Dataset


def load_data():
    """Load the MNIST dataset.

    Returns:
        Dataset: MNIST data
        (X_train, y_train), (X_test, y_test) = mnist.load_data()
    """

    print("Downloading MNIST dataset")
    (X_train, y_train), (X_test, y_test) = mnist.load_data()

    data = Dataset()
    data.train_images = X_train
    data.train_labels = y_train
    data.test_images = X_test
    data.test_labels = y_test
    data.classes = np.arange(10)
    return data
