# -*- coding: utf8 -*-
import threading
import numpy as np


class Iterator(object):
    """Base class for image data iterators.

    Every `Iterator` must implement the `_get_batches_of_transformed_samples`
    method.

    # Arguments
        n: Integer, total number of samples in the dataset to loop over.
        batch_size: Integer, size of a batch.
    """

    def __init__(self, n, batch_size, shuffle=True, seed=None):
        self.n = n
        self.batch_size = batch_size
        self.batch_index = 0
        self.total_batches_seen = 0
        self.lock = threading.Lock()
        self.index_array = None
        self.index_generator = self._flow_index()
        self.shuffle = shuffle
        self.__random_seed = np.random.RandomState(seed)

    def _set_index_array(self):
        self.index_array = np.arange(self.n)
        if self.shuffle:
            self.index_array = self.__random_seed.permutation(self.n)

    def __getitem__(self, idx):
        if idx >= len(self):
            raise ValueError(
                'Asked to retrieve element {idx}, '
                'but the Sequence '
                'has length {length}'.format(idx=idx, length=len(self)))

        self.total_batches_seen += 1
        if self.index_array is None:
            self._set_index_array()

        index_array = self.index_array[self.batch_size * idx: self.batch_size * (idx + 1)]
        return self._get_batches_of_transformed_samples(index_array)

    def __len__(self):
        if self.n == 0:
            return 0

        return (self.n + self.batch_size - 1) // self.batch_size  # round up

    def on_epoch_end(self):
        self._set_index_array()

    def reset(self):
        self.batch_index = 0

    def _flow_index(self):
        # Ensure self.batch_index is 0.
        self.reset()
        while 1:
            if self.batch_index == 0:
                self._set_index_array()

            current_index = (self.batch_index * self.batch_size) % self.n
            if self.n > current_index + self.batch_size:
                self.batch_index += 1
            else:
                self.batch_index = 0

            self.total_batches_seen += 1

            yield self.index_array[current_index:current_index + self.batch_size]

    def __iter__(self):
        # Needed if we want to do something like:
        # for x, y in data_gen.flow(...):
        return self

    def __next__(self, *args, **kwargs):
        return self.next(*args, **kwargs)

    def _get_batches_of_transformed_samples(self, index_array):
        """Gets a batch of transformed samples.

        # Arguments
            index_array: array of sample indices to include in batch.

        # Returns
            A batch of transformed samples.
        """
        raise NotImplementedError
