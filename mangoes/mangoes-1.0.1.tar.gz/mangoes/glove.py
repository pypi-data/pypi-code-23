#!/usr/bin/env python

import numpy as np
import random
import mangoes
import tqdm


class Glove:
    def __init__(self, source, dimensions, init_vectors=None, init_biases=None):
        self.source = source
        self.nb_words = len(source.words)
        self.dimensions = dimensions

        if init_vectors:
            self.words_vectors, self.contexts_vectors = init_vectors
        else:
            self.words_vectors = self._init_random(self.nb_words, self.dimensions)
            self.contexts_vectors = self._init_random(self.nb_words, self.dimensions)

        if init_biases:
            self.words_biases, self.contexts_biases = init_biases
        else:
            self.words_biases = self._init_random(self.nb_words)
            self.contexts_biases = self._init_random(self.nb_words)

        self.words_gradient_squared, self.words_biases_gradient_squared = self._init_gradient_squared()
        self.contexts_gradient_squared, self.contexts_biases_gradient_squared = self._init_gradient_squared()
        self.cost = []

    def _init_random(self, *shape):
        return (np.random.rand(shape) - 0.5) / self.dimensions

    def _init_gradient_squared(self):
        return np.ones((self.nb_words, self.dimensions), dtype=np.float64), np.ones(self.nb_words, dtype=np.float64)

    def train(self, iterations=100, alpha=0.75, initial_learning_rate=0.05):
        for _ in tqdm.tqdm(range(iterations)):
            self.cost.append(self._run_iter(learning_rate=initial_learning_rate, alpha=alpha))

    def _run_iter(self, learning_rate=0.05, x_max=100, alpha=0.75):
        global_cost = 0

        for i, j, cooccurrence in _data_generator(self.source):
            word_vector, context_vector = self.words_vectors[i], self.contexts_vectors[j]
            word_gradient_squared = self.words_gradient_squared[i]
            context_gradient_squared = self.contexts_gradient_squared[j]

            weight = (cooccurrence / x_max) ** alpha if cooccurrence < x_max else 1

            # Compute inner component of cost function, which is used in
            # both overall cost calculation and in gradient calculation
            # K = w_i^Tc_j + b_i + b_j - log(X_{ij})
            cost_inner = word_vector.dot(context_vector) + self.words_biases[i] + self.contexts_biases[j] - np.log(cooccurrence)

            # Update cost
            # Add weighted squared error to the global cost : J = f(X_{ij}) K^2
            global_cost += 0.5 * weight * (cost_inner ** 2)

            # Compute gradients
            word_gradient = weight * cost_inner * context_vector
            context_gradient = weight * cost_inner * word_vector
            word_bias_gradient = weight * cost_inner
            context_bias_gradient = weight * cost_inner

            # Adaptive gradient updates
            word_vector -= learning_rate * word_gradient / np.sqrt(word_gradient_squared)
            context_vector -= learning_rate * context_gradient / np.sqrt(context_gradient_squared)
            self.words_biases[i] -= learning_rate * word_bias_gradient / np.sqrt(self.words_biases_gradient_squared[i])
            self.contexts_biases[j] -= learning_rate * context_bias_gradient / np.sqrt(self.contexts_biases_gradient_squared[j])

            # Update squared gradient sums
            word_gradient_squared += np.square(word_gradient)
            context_gradient_squared += np.square(context_gradient)
            self.words_biases_gradient_squared[i] += word_bias_gradient ** 2
            self.contexts_biases_gradient_squared[j] += context_bias_gradient ** 2

        return global_cost


def train_glove(source, dimensions,
                init_vectors=None,
                iterations=100, alpha=0.75, initial_learning_rate=0.5,
                add_context_vectors=False):
    vocab_size = len(source.words)

    words_vectors, words_biases, words_gradient_squared, words_biases_gradient_squared = _init(dimensions, vocab_size)
    contexts_vectors, contexts_biases, contexts_gradient_squared, contexts_biases_gradient_squared = _init(dimensions, vocab_size)

    if init_vectors:
        words_vectors, contexts_vectors = init_vectors

    cost = []

    for _ in tqdm.tqdm(range(iterations)):
        cost.append(_run_iter(source,
                              words_vectors, contexts_vectors,
                              words_biases, contexts_biases,
                              words_gradient_squared, contexts_gradient_squared,
                              words_biases_gradient_squared, contexts_biases_gradient_squared,
                              learning_rate=initial_learning_rate, alpha=alpha))

    if add_context_vectors:
        return mangoes.Embeddings(source.words, mangoes.utils.arrays.Matrix.factory(words_vectors + contexts_vectors))

    return mangoes.Embeddings(source.words, mangoes.utils.arrays.Matrix.factory(words_vectors))


def _init(dimensions, vocab_size):
    words_vectors = (np.random.rand(vocab_size, dimensions) - 0.5) / dimensions
    biases = (np.random.rand(vocab_size) - 0.5) / dimensions
    words_gradient_squared = np.ones((vocab_size, dimensions), dtype=np.float64)
    biases_gradient_squared = np.ones(vocab_size, dtype=np.float64)
    return  words_vectors, biases, words_gradient_squared, biases_gradient_squared


def _data_generator(cooccurrence):
    A = cooccurrence.matrix.tocoo()
    shuffled_indices = np.arange(A.nnz)
    random.shuffle(shuffled_indices)
    for i in shuffled_indices:
        yield A.row[i], A.col[i], A.data[i]


def _run_iter(source,
              words_vectors, contexts_vectors,
              words_biases, contexts_biases,
              words_gradient_squared, contexts_gradient_squared,
              words_biases_gradient_squared, contexts_biases_gradient_squared,
              learning_rate=0.05, x_max=100, alpha=0.75):
    global_cost = 0

    for i, j, cooccurrence in _data_generator(source):
        word_vector, context_vector = words_vectors[i], contexts_vectors[j]
        word_gradient_squared, context_gradient_squared = words_gradient_squared[i], contexts_gradient_squared[j]
        weight = (cooccurrence / x_max) ** alpha if cooccurrence < x_max else 1

        # Compute inner component of cost function, which is used in
        # both overall cost calculation and in gradient calculation
        # K = w_i^Tc_j + b_i + b_j - log(X_{ij})
        cost_inner = word_vector.dot(context_vector) + words_biases[i] + contexts_biases[j] - np.log(cooccurrence)

        # Update cost
        # Add weighted squared error to the global cost : J = f(X_{ij}) K^2
        global_cost += 0.5 * weight * (cost_inner ** 2)

        # Compute gradients
        word_gradient = weight * cost_inner * context_vector
        context_gradient = weight * cost_inner * word_vector
        word_bias_gradient = weight * cost_inner
        context_bias_gradient = weight * cost_inner

        # Adaptive gradient updates
        word_vector -= learning_rate * word_gradient / np.sqrt(word_gradient_squared)
        context_vector -= learning_rate * context_gradient / np.sqrt(context_gradient_squared)
        words_biases[i] -= learning_rate * word_bias_gradient / np.sqrt(words_biases_gradient_squared[i])
        contexts_biases[j] -= learning_rate * context_bias_gradient / np.sqrt(contexts_biases_gradient_squared[j])

        # Update squared gradient sums
        word_gradient_squared += np.square(word_gradient)
        context_gradient_squared += np.square(context_gradient)
        words_biases_gradient_squared[i] += word_bias_gradient ** 2
        contexts_biases_gradient_squared[j] += context_bias_gradient ** 2


    return global_cost
