"""
Segmentation
-----------

A widget for audio clips segmentation
"""

import Orange.data
from Orange.data import DiscreteVariable
from Orange.widgets import widget, gui, settings
from PyQt4.QtGui import *
from PyQt4.QtCore import *


import time
import numpy

from ..segmentation import Segmentation

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'


class OWSegmentationn(widget.OWWidget):
    name = "Segmentation"
    description = "Segment audio clips on segments calculate by sliding window"
    priority = 3
    icon = "icons/sliding_window.png"

    inputs = [("Data", Orange.data.Table, "set_data")]

    window_size = settings.Setting(1)
    overlap = settings.Setting(1)

    outputs = [("Segmentation", Orange.data.Table)]

    want_main_area = False

    data = None

    def __init__(self):
        super().__init__()

        self.tmp_dir_id = str(time.time()).split(".")[-1]
        self.new_tmp_dirs = []

        info_box = gui.widgetBox(self.controlArea, "Info")
        self.info = gui.widgetLabel(
            info_box, 'No data on input yet, waiting to get something.')

        parameters_box = gui.widgetBox(self.controlArea, 'Parameters')

        self.window_size_spin = gui.spin(
            parameters_box,
            self,
            "window_size",
            minv=0.01,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Window size [s]: ",
            spinType=float,
            decimals=2)
        self.overlap_spin = gui.spin(
            parameters_box,
            self,
            "overlap",
            minv=0.01,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Overlap [s]: ",
            spinType=float,
            decimals=2)

        self.segment_button = gui.button(
            self.controlArea,
            self,
            "Segment",
            callback=lambda: self.call_segmetation())

    def set_data(self, dataset):
        """
        Set data from input

        :param dataset: input data
        :return: Void
        """

        if dataset is not None:
            self.info.setText('%d instances in input data set' % len(dataset))
            self.data = dataset

        else:
            self.info.setText(
                'No data on input yet, waiting to get something.')
            self.send("Segmentation", None)

    def call_segmetation(self):
        """
        Segment all recordings and create new Orange table

        :return: Void
        """

        if self.data is None:
            print(self.window_size)
            return

        error = None

        try:
            segmentation = Segmentation()
            if self.window_size > max(self.data.metas[:, -2]):
                self.info.setStyleSheet(error_red)
                self.info.setText(
                    "Window size must be lower than largest sound clip!")
                return
            elif self.overlap > max(self.data.metas[:, -2]):
                self.info.setStyleSheet(error_red)
                self.info.setText(
                    "Overlap must be lower than largest sound clip!")
                return
            data = segmentation.segment_all(
                self.data, self.window_size, self.overlap, self.tmp_dir_id)

        except Exception as ex:
            error = ex

        if not error:

            self.info.setStyleSheet(success_green)
            self.info.setText("Segmentation successful")

            if data[0] != []:
                Y = DiscreteVariable.make(
                    "Target class",
                    values=self.data.domain.class_var.values,
                    ordered=True)
            else:
                Y = None

            segment_var = Orange.data.StringVariable("segment name")
            sound_var = Orange.data.StringVariable("sound")
            sound_var.attributes["type"] = "sound"
            size_var = Orange.data.ContinuousVariable(
                "segment size", number_of_decimals=0)
            length_var = Orange.data.ContinuousVariable(
                "segment length", number_of_decimals=2)
            framerate_var = Orange.data.ContinuousVariable(
                "segment framerate", number_of_decimals=0)

            domain = Orange.data.Domain(
                [], [Y] if Y is not None else [], [
                    segment_var, sound_var, size_var, length_var, framerate_var])

            if len(data[0]):
                table = Orange.data.Table.from_numpy(domain, numpy.empty(
                    (len(data[0]), 0), dtype=float), data[0], data[1])
            else:
                table = None

            self.send("Segmentation", table)

        if error:
            self.info.setStyleSheet(error_red)
            self.info.setText("An error occurred:\n{}".format(error))
            return

    def onDeleteWidget(self):
        """
        Delete temporarily written audio clips

        :return: Void
        """

        if self.new_tmp_dirs != []:
            import shutil
            for i in self.new_tmp_dirs:
                shutil.rmtree(i)
