from PyQt4.QtGui import *
from PyQt4.QtCore import *

import Orange.data
from Orange.data import Domain, Table, DiscreteVariable

from Orange.widgets import widget, gui
from scipy.io.wavfile import read
import numpy

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'


class OWAudioToTable(widget.OWWidget):
    name = "Audio_to_Table"
    description = "Read audio files and return raw audio data"
    icon = "icons/min_max_avg.png"
    priority = 5

    inputs = [("Data", Orange.data.Table, "set_data")]
    outputs = [("Audio", Orange.data.Table)]

    want_main_area = False

    discrete_atributes = []

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, "Info")
        self.info = gui.widgetLabel(
            box, 'No data on input yet, waiting to get something.')

    def set_data(self, dataset):
        """
        Set data from input

        :param dataset: input data
        :return: Void
        """

        if dataset is not None:

            self.info.setText('%d instances in input data set' % len(dataset))

            error = None
            try:
                if dataset.X != []:
                    self.send("Audio", dataset)
                else:
                    self.make_orange_table(dataset)

            except Exception as ex:
                error = ex

            if not error:
                self.info.setStyleSheet(success_green)
                self.info.setText("Task successfully completed")

            if error:
                self.info.setStyleSheet(error_red)
                self.info.setText("An error occurred:\n{}".format(error))
                return

        else:
            self.info.setText(
                'No data on input yet, waiting to get something.')
            self.send("Audio", None)

    def make_orange_table(self, dataset):
        """
        Make Orange table with raw audio data and send it to output

        :param dataset: input dataset
        :return: Void
        """

        X = []
        for i in dataset.metas:
            import os
            if os.path.isfile(i[1]):
                filename = i[1]
            else:
                filename = i[1].split(".wav")[0]

            framerate, data = read(filename)
            if len(data.shape) > 1:
                data = data[:, 0]
            X.append(data)

        X = self.make_square_array(numpy.array(X), max(dataset.metas[:, 2]))
        data_vars = [Orange.data.ContinuousVariable.make(
            'n{:d}'.format(i)) for i in range(len(X[0]))]

        if dataset.Y != []:
            Y = DiscreteVariable.make(
                "Category",
                values=dataset.domain.class_var.values,
                ordered=True)
        else:
            Y = None

        self.domain = Domain(
            attributes=data_vars,
            class_vars=Y,
            metas=dataset.domain.metas)

        orange_table = Table(
            self.domain,
            numpy.array(X),
            dataset.Y,
            dataset.metas)
        self.send("Audio", orange_table)

    def make_square_array(self, data, maximum):
        """
        Make square array (fill with zeros) from raw audio dataset

        :param data: raw audio data
        :param maximum: maximum length of audio clip
        :return: square X array filled by zeros
        """

        square_X = numpy.zeros((len(data), maximum))
        for i in range(len(data)):
            square_X[i, 0:len(data[i])] = data[i]

        return square_X
