import wave
import numpy as np
import os
import glob
from Orange.data import Domain, Table, ContinuousVariable, DiscreteVariable, StringVariable


class ImportData:

    def read_dir(self, file_path):
        """
        :param file_path: path to file
        :return: declaration of variable initializes in __init__----square X, Y, file names, framerates
        """

        raw_data = self.import_wav(file_path)

        data = [raw_data[0], raw_data[1], raw_data[2]]

        return data

    def sort_data(self, data):
        """
        :param data: list of X, Y, metas and framerate wich must be sorted by Y
        :return: sorted X, Y, metas and framerate by Y
        """

        self.discrete_atributes = sorted(self.discrete_atributes)
        X, Y, metas, framerate = [], [], [], []

        for i in self.discrete_atributes:
            for x in range(len(data)):
                if i == data[x][1]:
                    X.append(data[x][0])
                    Y.append(self.discrete_atributes.index(i))
                    metas.append(data[x][2])
                    framerate.append(data[x][3])

        return X, Y, metas, framerate

    def make_square_array(self, sorted_data):
        """
        :param sorted_data: sorted X, Y, metas and framerate by Y
        :return: square X array filled by zeros
        """

        maximum = self.calc_max(sorted_data[0])

        square_X = np.zeros((len(sorted_data[0]), maximum))
        for i in range(len(sorted_data[0])):
            square_X[i, 0:len(sorted_data[0][i])] = sorted_data[0][i]

        return square_X

    def pre_segment_data(self, data):

        segment_data = []
        avg = int(self.calc_avg(data))
        print(avg)
        for i in data:
            if len(i[0]) > avg:
                iterations = int(len(i[0]) / avg)
                for x in range(iterations):
                    segment_data.append(
                        [i[0][x * avg:(x + 1) * avg], i[1], i[2], i[3]])
                segment_data.append(
                    [i[0][(iterations) * avg: len(i[0])], i[1], i[2], i[3]])
            else:
                segment_data.append(i)
        return segment_data

    def calc_max(self, X):
        """
        :param X: raw data
        :return: maximum of largest row
        """

        maximum = 0
        for i in X:
            tmp = len(i)
            if(tmp > maximum):
                maximum = tmp
        return maximum

    def calc_avg(self, data):
        return sum([len(i[0]) for i in data]) / len(data)

    def import_wav(self, file_path):
        """
        :param file_path: path to file
        :return: .wav data as np array
        """

        fp = wave.open(file_path)
        nchan = fp.getnchannels()
        N = fp.getnframes()
        dstr = fp.readframes(N * nchan)
        data = np.fromstring(dstr, np.int16)
        data = np.reshape(data, (-1, nchan))

        file_name = os.path.split(file_path)[-1]
        print(len(data[:, 0]))
        return data[:, 0], file_name, fp.getframerate()
