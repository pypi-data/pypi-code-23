"""
Filtering
-----------

A widget for filtering audio clips
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import Orange.data
from Orange.widgets import widget, gui, settings

import biosppy.signals.tools as st
from scipy.io.wavfile import read, write
import os
import time
import numpy

filter_designs = [
    "Finite Impulse Response",
    "Butterworth",
    "Chebyshev 1",
    "Chebyshev 2",
    "Elliptic",
    "Bessel"
]

band_types = [
    "Low-pass",
    "High-pass",
    "Band-pass",
    "Band-stop"
]

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'


class OWFiltering(widget.OWWidget):
    name = "Filtering"
    description = "Filter audio clips"
    priority = 2
    icon = "icons/filtering.png"

    inputs = [("Data", Orange.data.Table, "set_data")]
    filter_design_id = settings.Setting(0)
    band_type_id = settings.Setting(0)

    first_cutoff = settings.Setting(1000)
    second_cutoff = settings.Setting(1000)
    filter_order = settings.Setting(10)
    maximum_ripple = settings.Setting(10)
    minimum_attenuation = settings.Setting(10)

    outputs = [("Filtered data", Orange.data.Table)]

    want_main_area = False

    data = None

    def __init__(self):
        super().__init__()

        self.tmp_dir_id = str(time.time()).split(".")[-1]
        self.new_tmp_dirs = []

        info_box = gui.widgetBox(self.controlArea, "Info")
        self.info = gui.widgetLabel(
            info_box, 'No data on input yet, waiting to get something.')

        self.filter_designs_combo = gui.comboBox(
            self.controlArea,
            self,
            "filter_design_id",
            box="Filter designs",
            items=[
                m for m in filter_designs],
        )
        self.filter_designs_combo.activated.connect(self.onDesignChange)

        self.band_types_combo = gui.comboBox(
            self.controlArea,
            self,
            "band_type_id",
            box="Band types",
            items=[
                m for m in band_types],
        )
        self.band_types_combo.activated.connect(self.onTypeChange)

        parameters_box = gui.widgetBox(self.controlArea, 'Parameters')
        self.first_cutoff_spin = gui.spin(
            parameters_box,
            self,
            "first_cutoff",
            minv=1,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="First cutoff frequency [Hz]: ",
            spinType=float,
            decimals=2)
        self.second_cutoff_spin = gui.spin(
            parameters_box,
            self,
            "second_cutoff",
            minv=1,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Second cutoff frequency [Hz]: ",
            spinType=float,
            decimals=2)
        self.filter_order_spin = gui.spin(
            parameters_box,
            self,
            "filter_order",
            minv=1,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Order: ")
        self.maximum_ripple_spin = gui.spin(
            parameters_box,
            self,
            "maximum_ripple",
            minv=1,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Maximum ripple [dB]: ",
            spinType=float,
            decimals=2)
        self.minimum_attenuation_spin = gui.spin(
            parameters_box,
            self,
            "minimum_attenuation",
            minv=1,
            maxv=10000,
            controlWidth=80,
            alignment=Qt.AlignRight,
            label="Minimum attenuation [dB]: ",
            spinType=float,
            decimals=2)

        self.filter_button = gui.button(
            self.controlArea,
            self,
            "Filter",
            callback=lambda: self.call_filter(
                self.filter_designs_combo.currentText(),
                self.band_types_combo.currentText(),
                self.first_cutoff,
                self.second_cutoff,
                self.filter_order,
                self.maximum_ripple,
                self.minimum_attenuation))

        self.onDesignChange()

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
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.send("Filtered data", None)

    def allSpinHandle(self, handle):
        """
        Helper function which handle all spines at once

        :param handle: handle parameter (true -> enable, false -> disable)
        :return: Void
        """

        self.first_cutoff_spin.setEnabled(handle)
        self.second_cutoff_spin.setEnabled(handle)
        self.filter_order_spin.setEnabled(handle)
        self.maximum_ripple_spin.setEnabled(handle)
        self.minimum_attenuation_spin.setEnabled(handle)

    def onDesignChange(self):
        """
        When the desgin changes, it changes the options of the parameters

        :return: Void
        """

        self.allSpinHandle(True)
        if self.filter_design_id == 0 or self.filter_design_id == 1 or self.filter_design_id == 5:
            self.second_cutoff_spin.setEnabled(False)
            self.maximum_ripple_spin.setEnabled(False)
            self.minimum_attenuation_spin.setEnabled(False)
        elif self.filter_design_id == 2:
            self.second_cutoff_spin.setEnabled(False)
            self.minimum_attenuation_spin.setEnabled(False)
        elif self.filter_design_id == 3:
            self.second_cutoff_spin.setEnabled(False)
            self.maximum_ripple_spin.setEnabled(False)
        self.onTypeChange()

    def onTypeChange(self):
        """
        When the type changes, it changes the options of the parameters

        :return: Void
        """

        if self.band_type_id == 2 or self.band_type_id == 3:
            self.second_cutoff_spin.setEnabled(True)
        else:
            self.second_cutoff_spin.setEnabled(False)

    def call_filter(
            self,
            filter_type,
            filter_band,
            first_cutoff,
            second_cutoff,
            order,
            max_ripple,
            min_attenuation):
        """
        Call specified filter function on all audio clips

        :param filter_type: type of filter
        :param filter_band:  band of filter
        :param first_cutoff: first cutoff frequency
        :param second_cutoff: second cutoff frequency
        :param order: filter order
        :param max_ripple: the maximum ripple
        :param min_attenuation: the minimum attenuatio
        :return: Void
        """

        if self.data is None:
            return

        filterBand = (''.join(c for c in filter_band if c not in "-")).lower()
        filterType = self.convertTypeToStr(filter_type)

        error = None

        self.X = []
        self.metas = []

        try:
            for i in range(len(self.data.metas)):
                if self.data.X != []:
                    input_data = self.data.X[i]
                else:
                    input_data = read(self.data.metas[i][1])[1]
                    if len(input_data.shape) > 1:
                        input_data = input_data[:, 0]

                if filterType == "FIR" or filterType == "butter" or filterType == "bessel":
                    if filterBand == "lowpass" or filterBand == "highpass":
                        filtered = st.filter_signal(input_data,
                                                    ftype=filterType,
                                                    band=filterBand,
                                                    order=order,
                                                    frequency=first_cutoff,
                                                    sampling_rate=self.data.metas[i][-1])
                    else:
                        filtered = st.filter_signal(input_data, ftype=filterType, band=filterBand, order=order,
                                                    frequency=[first_cutoff, second_cutoff],
                                                    sampling_rate=self.data.metas[i][-1])
                elif filterType == "cheby1":
                    if filterBand == "lowpass" or filterBand == "highpass":
                        filtered = st.filter_signal(input_data,
                                                    ftype=filterType,
                                                    band=filterBand,
                                                    order=order,
                                                    frequency=first_cutoff,
                                                    sampling_rate=self.data.metas[i][-1],
                                                    rp=max_ripple)
                    else:
                        filtered = st.filter_signal(input_data, ftype=filterType, band=filterBand, order=order,
                                                    frequency=[first_cutoff, second_cutoff], sampling_rate=self.data.metas[i][-1],
                                                    rp=max_ripple)
                elif filterType == "cheby2":
                    if filterBand == "lowpass" or filterBand == "highpass":
                        filtered = st.filter_signal(input_data,
                                                    ftype=filterType,
                                                    band=filterBand,
                                                    order=order,
                                                    frequency=first_cutoff,
                                                    sampling_rate=self.data.metas[i][-1],
                                                    rs=min_attenuation)
                    else:
                        filtered = st.filter_signal(input_data, ftype=filterType, band=filterBand, order=order,
                                                    frequency=[first_cutoff, second_cutoff], sampling_rate=self.data.metas[i][-1],
                                                    rs=min_attenuation)

                else:
                    if filterBand == "lowpass" or filterBand == "highpass":
                        filtered = st.filter_signal(input_data,
                                                    ftype=filterType,
                                                    band=filterBand,
                                                    order=order,
                                                    frequency=first_cutoff,
                                                    sampling_rate=self.data.metas[i][-1],
                                                    rp=max_ripple,
                                                    rs=min_attenuation)
                    else:
                        filtered = st.filter_signal(input_data,
                                                    ftype=filterType,
                                                    band=filterBand,
                                                    order=order,
                                                    frequency=[first_cutoff,
                                                               second_cutoff],
                                                    sampling_rate=self.data.metas[i][-1],
                                                    rp=max_ripple,
                                                    rs=min_attenuation)

                self.new_tmp_dir = os.path.dirname(
                    self.data.metas[i][1]) + os.sep + "filtered-" + self.tmp_dir_id + os.sep

                if not os.path.exists(self.new_tmp_dir):
                    os.makedirs(self.new_tmp_dir)
                    self.new_tmp_dirs.append(self.new_tmp_dir)

                filename = self.new_tmp_dir + self.data.metas[i][0] + ".wav"
                self.metas.append([self.data.metas[i][0],
                                   filename,
                                   self.data.metas[i][2],
                                   self.data.metas[i][3],
                                   self.data.metas[i][4]])

                data = filtered["signal"]
                data = data / data.max()
                data = data * (2 ** 15 - 1)
                data = data.astype(numpy.int16)
                write(filename, self.data.metas[i][-1], data)

        except Exception as ex:
            error = ex

        if not error:
            self.info.setStyleSheet(success_green)
            self.info.setText(
                filter_type +
                " " +
                filter_band +
                " " +
                "filter successful!")
            orange_table = Orange.data.Table.from_numpy(
                self.data.domain, numpy.empty((len(self.data.Y), 0), dtype=float),
                self.data.Y, self.metas
            )

            self.send("Filtered data", orange_table)
        if error:
            self.info.setStyleSheet(error_red)
            self.info.setText("An error occurred:\n{}".format(error))
            return

    def convertTypeToStr(self, filter_type):
        """
        Helper function which convert specified type of filter in a coded string

        :param filter_type: type of filter
        :return: coded type of filter
        """

        if filter_type == "Finite Impulse Response":
            typeStr = "FIR"
        elif filter_type == "Butterworth":
            typeStr = "butter"
        elif filter_type == "Chebyshev 1":
            typeStr = "cheby1"
        elif filter_type == "Chebyshev 2":
            typeStr = "cheby2"
        elif filter_type == "Elliptic":
            typeStr = "ellip"
        else:
            typeStr = "bessel"

        return typeStr

    def onDeleteWidget(self):
        """
        Delete temporarily written audio clips

        :return: Void
        """

        if self.new_tmp_dirs != []:
            import shutil
            for i in self.new_tmp_dirs:
                shutil.rmtree(i)
