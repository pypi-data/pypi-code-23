import sys
import numpy
import collections

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import Orange.data
from Orange.data import ContinuousVariable, Domain, StringVariable, Table, DiscreteVariable
from Orange.widgets import widget, gui

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'


class OWMinMaxAvgWidget(widget.OWWidget):
    name = "Min/Avg/Max"
    description = "Calculate min, max and avg of classifiers"
    icon = "icons/min_max_avg.png"
    priority = 5

    inputs = [("Data", Orange.data.Table, "set_data")]
    outputs = [("Min/Max/Avg features", Orange.data.Table)]

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
                classification_dict = self.make_classification_dict(dataset)

                if classification_dict is None:
                    self.send("Min/Max/Avg features", None)
                    self.info.setText(
                        "Please get classification probabilities")
                    return

            except Exception as ex:
                error = ex

            if not error:
                self.info.setStyleSheet(success_green)
                self.info.setText("Task successfully completed")

                data = self.process_data(classification_dict)
                orange_table = self.make_orange_table(
                    data[0], data[1], data[2], dataset.domain.metas)
                self.send("Min/Max/Avg features", orange_table)

            if error:
                self.info.setStyleSheet(error_red)
                self.info.setText("An error occurred:\n{}".format(error))
                return

        else:
            self.info.setText(
                'No data on input yet, waiting to get something.')
            self.send("Min/Max/Avg features", None)

    def make_classification_dict(self, dataset):
        """
        Concatenate all segments which belongs to one audio recording and create dictionary
        with min, max and avg classification probabilities

        :param dataset: input data
        :return: dictionary with min, max, avg classification probabilities, counter and class value
        """

        classification_dict = dict()
        meta_attrs = dataset.domain.metas

        for i in dataset:
            metas = i.metas
            class_value = i.get_class()
            tmp = metas[0].split("_")
            segment_name = ""
            for i in range(len(tmp) - 1):
                segment_name += tmp[i] + "_"
            segment_name = segment_name[:-1] + ".wav"
            print(segment_name)
            if segment_name not in classification_dict:
                classification_dict[segment_name] = dict()

            for x in range(5, len(metas)):
                if str(type(meta_attrs[x])) == "ContinuousVariable":
                    if meta_attrs[x] not in classification_dict[segment_name]:
                        classification_dict[segment_name][meta_attrs[x]] = collections.defaultdict(
                            list)
                        classification_dict[segment_name][meta_attrs[x]] = [
                            0, 2, 0, 0, str(class_value)]
                    classification_dict[segment_name][meta_attrs[x]
                                                      ][0] += metas[x]
                    classification_dict[segment_name][meta_attrs[x]][1] = min(
                        classification_dict[segment_name][meta_attrs[x]][1], metas[x])
                    classification_dict[segment_name][meta_attrs[x]][2] = max(
                        classification_dict[segment_name][meta_attrs[x]][2], metas[x])
                    classification_dict[segment_name][meta_attrs[x]][3] += 1

        return classification_dict

    def process_data(self, classification_dict):
        """
        Create and fill 3 list described in return section

        :param classification_dict: filled dictionary with min, max, avg classification probabilities, counter and class value
        :return: 3 list -> data (classification probabilities), Y (class values), metas (file names)
        """

        metas, data, Y = [], [], []

        for key, value in classification_dict.items():

            class_value = None
            tmp_data = []

            for x, y in value.items():
                tmp_data += [y[1], y[2], y[0] / float(y[3])]
                class_value = y[-1]

            if(class_value not in self.discrete_atributes):
                self.discrete_atributes.append(class_value)
                Y.append(self.discrete_atributes.index(class_value))
            else:
                Y.append(self.discrete_atributes.index(class_value))

            metas.append([key])
            data.append(tmp_data)

        return numpy.array(data), numpy.array(Y), numpy.array(metas)

    def make_orange_table(self, data, Y, file_names, domain_metas):
        """
        Make Orange table with min, max and avg classification probabilities

        :param data: min, max and avg classification probabilities
        :param Y: category values
        :param file_names: name of files
        :param domain_metas: all meta attributes from domain
        :return: orange table with category, file name, min, max and avg classification probabilities
        """

        category = DiscreteVariable(
            "Target class", values=self.discrete_atributes)

        attributes = []

        for i in range(5, len(domain_metas)):
            if str(type(domain_metas[i])) == "ContinuousVariable":
                attributes.append(ContinuousVariable.make(
                    "MIN_" + str(domain_metas[i].name)))
                attributes.append(ContinuousVariable.make(
                    "MAX_" + str(domain_metas[i].name)))
                attributes.append(ContinuousVariable.make(
                    "AVG_" + str(domain_metas[i].name)))

        METAS = [('File name', 'file_name')]
        meta_attr = [StringVariable.make(meta[0]) for meta in METAS]

        self.domain = Domain(attributes, class_vars=category, metas=meta_attr)

        orange_table = Table(self.domain, data, Y, file_names)

        return orange_table
