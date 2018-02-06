from collections import deque
from itertools import islice
import numpy as np
from scipy.io.wavfile import read, write
import os


class Segmentation:

    def __init__(self):
        self.Y = []
        self.metas = []
        self.new_tmp_dirs = []

    def segment_all(self, data, window_size, overlap, tmp_dir_id):
        """
        Call segmentation function on all audio clips

        :param data: input data
        :param window_size: window size
        :param overlap: overlap
        :param tmp_dir_id: hash of temporary directory
        :return: segmented data
        """

        for i in range(len(data.metas)):
            if os.path.isfile(data.metas[i][1]):
                filename = data.metas[i][1]
            else:
                filename = data.metas[i][1].split(".wav")[0]
            framerate, X = read(filename)
            if len(X.shape) > 1:
                X = X[:, 0]
            self.segmentation(X, data.metas[i], data.Y[i], window_size, overlap, tmp_dir_id)

        return np.array(self.Y), self.metas, self.new_tmp_dirs

    def segmentation(self, data, metas, target_class, window_size, overlap, tmp_dir_id):
        """
        Call sliding_window function to segment audio clip and temporarily write them in the specified folder

        :param data: data for one sound clip
        :param metas: meta data
        :param target_class: sound clip category
        :param window_size: window size
        :param overlap: overlap
        :param tmp_dir_id: hash of temporary directory
        :return: Void -> append data to variables declared in __init__
        """

        if window_size == "" or window_size == "0":
            window_size = 1
        if overlap == "" or overlap == "0":
            overlap = 1
        window_size = int(metas[-1] * float(window_size))
        overlap = int(metas[-1] * float(overlap))

        segments = self.sliding_window(data, window_size, overlap)
        counter = 1

        for i in segments:
            c = []
            for x in i:
                c.append(x)
            tmp = [x for x in c if x != None and x != 0]
            if len(tmp) == 0:
                continue
            array_len = len(c)
            if c.count(None) > 0:
                c = [0 if x is None else x for x in c]
            elif c.count(0) >= array_len / 2:
                continue

            new_tmp_dir = os.path.dirname(metas[1]) + os.sep + "segmented-" + tmp_dir_id + os.sep
            if not os.path.exists(new_tmp_dir):
                os.makedirs(new_tmp_dir)
                self.new_tmp_dirs.append(new_tmp_dir)

            filename = new_tmp_dir + metas[0] + "_" + str(counter) + ".wav"
            write(filename, metas[-1], np.array(c))

            self.metas.append([metas[0] + "_" + str(counter), filename, window_size, float(window_size) / float(metas[-1]), metas[-1]])
            self.Y.append(target_class)

            counter += 1

    def sliding_window(self, iterable, size=2, step=1, fillvalue=None):
        """
        Implemented sliding window algorithm

        :param iterable: data
        :param size: window size
        :param step: overlap
        :param fillvalue: fill value
        :return: iterator of segmented audio data
        """

        if size < 0 or step < 1:
            raise ValueError
        it = iter(iterable)
        q = deque(islice(it, size), maxlen=size)
        if not q:
            return  # empty iterable or size == 0
        q.extend(fillvalue for _ in range(size - len(q)))  # pad to size
        while True:
            yield iter(q)  # iter() to avoid accidental outside modifications
            try:
                q.append(next(it))
            except StopIteration:  # Python 3.5 pep 479 support
                return
            q.extend(next(it, fillvalue) for _ in range(step - 1))
