"""
Module to load the Fashion MNIST database of handwritten digits
See https://github.com/zalandoresearch/fashion-mnist

Fashion-MNIST is a dataset of Zalando's article images—consisting of a training set of 60,000 examples and a test set
of 10,000 examples. Each example is a 28x28 grayscale image, associated with a label from 10 classes. We intend
Fashion-MNIST to serve as a direct drop-in replacement for the original MNIST dataset for benchmarking machine learning
algorithms. It shares the same image size and structure of training and testing splits.
"""

import numpy as np
from keras.datasets import fashion_mnist

from dlt.utils import Dataset

Fashion_mnist_labels = np.array([
    "T-short/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot"
])


def load_data():
    """Load the Fashion-MNIST dataset.

    Returns:
        Dataset: Fashion-MNIST data
        (X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()
    """

    print("Downloading Fashion-MNIST dataset")
    (X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()

    data = Dataset()
    data.train_images = X_train
    data.train_labels = y_train
    data.test_images = X_test
    data.test_labels = y_test
    data.classes = Fashion_mnist_labels
    return data
