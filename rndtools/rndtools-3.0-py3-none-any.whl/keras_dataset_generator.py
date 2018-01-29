import codecs
import itertools
import json
import os
import pickle
from abc import abstractmethod, abstractproperty

import hickle
import numpy as np


class PartsDoNotExist(Exception):
    pass


class DataSerializer():
    def __init__(self, filepath):
        self.fl = filepath

    def pickle_out(self, data):
        out_s = open(self.fl, 'wb')
        pickle.dump(data, out_s, protocol=2)
        out_s.close()

    def hickle_out(self, data):
        hickle.dump(data, self.fl)

    def hickle_in(self):
        return hickle.load(self.fl)

    def json_out(self, data):
        with open(self.fl, 'w') as f:
            json.dump(data, f)

    def pickle_in(self):
        in_s = open(self.fl, 'rb')
        return pickle.load(in_s)

    def json_in(self):
        with codecs.open(self.fl, 'r', encoding='utf8') as f:
            return json.load(f)

    def json_in_chunks(self, chunk_size):
        with open(self.fl) as f:
            out = json.load(f)
            for i in xrange(0, len(out), chunk_size):
                yield out[i:i + chunk_size]


class Dataset(object):
    @abstractproperty
    def path(self):
        pass


class DatasetInPartsGenerator(Dataset):
    def __init__(self, dir_path, batch_size=1):
        self.parts_to_iterate = None

        self.dir_path = dir_path
        self.batch_size = batch_size

        part_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
        parts_serializers = [DataSerializer(f) for f in part_files]

        if len(parts_serializers) == 0:
            raise PartsDoNotExist()

        self.parts_serializers = itertools.cycle(parts_serializers)

    @property
    def path(self):
        return self.dir_path

    def _change_parts_serializer(self):
        serializer = next(self.parts_serializers)

        X_part, Y_part = serializer.hickle_in()

        parts_to_split = X_part.shape[0] / self.batch_size

        self.parts_to_iterate = itertools.izip(np.array_split(X_part, parts_to_split), np.array_split(Y_part, parts_to_split))

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        try:
            x, y = next(self.parts_to_iterate)
        except (StopIteration, TypeError):
            self._change_parts_serializer()
            x, y = next(self.parts_to_iterate)

        return x, y
