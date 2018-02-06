"""
Feature Extraction
-----------

A widget for audio feature extraction
"""
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import Orange.data
from Orange.data import ContinuousVariable, Domain, Table, DiscreteVariable


from ..feature_extraction import FeatureExtraction
from scipy.io.wavfile import read

from Orange.widgets import widget, gui, settings
import os
import numpy

feature_types = [
    "Emotions",
    "MFCC",
    "PLP",
    "Chroma",
    "pyAudio"
]

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'


class OWFeatureExtraction(widget.OWWidget):
    name = "Feature Extraction"
    description = "Extract features from audio clips"
    priority = 4
    icon = "icons/feature.png"

    inputs = [("Data", Orange.data.Table, "set_data")]

    feature_type_id = settings.Setting(0)

    outputs = [("Extracted features", Orange.data.Table)]

    want_main_area = False

    data = None

    def __init__(self):
        super().__init__()
        info_box = gui.widgetBox(self.controlArea, "Info")
        self.info = gui.widgetLabel(
            info_box, 'No data on input yet, waiting to get something.')

        self.filter_designs_combo = gui.comboBox(
            self.controlArea,
            self,
            "feature_type_id",
            box="Feature types",
            items=[
                m for m in feature_types],
        )

        self.filter_button = gui.button(
            self.controlArea,
            self,
            "Extract features",
            callback=lambda: self.call_feature_extraction(
                self.feature_type_id))

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
            self.send("Extracted features", None)

    def call_feature_extraction(self, id):
        """
        :param id: feature id
        :return: Void -> load data with extracted features to Orange table
        """
        if self.data is None:
            return

        error = None
        feature_extracted_data = []
        try:
            feature_extraction = FeatureExtraction()

            for i in range(len(self.data.metas)):
                if os.path.isfile(self.data.metas[i][1]):
                    filename = self.data.metas[i][1]
                else:
                    filename = self.data.metas[i][1].split(".wav")[0]
                if id == 0:
                    array = feature_extraction.extract_emobase_features(
                        filename)
                elif id == 1 or id == 2:
                    array = feature_extraction.extract_mfcc_plp_features(
                        filename, id)
                elif id == 3:
                    array = feature_extraction.extract_chroma_features(
                        filename)
                else:
                    framerate, data = read(filename)
                    array = feature_extraction.extract_all_mean_features(
                        data, framerate)

                feature_extracted_data.append(array)

            self.X = numpy.array(feature_extracted_data)

        except Exception as ex:
            error = ex

        if not error:
            self.info.setStyleSheet(success_green)
            self.info.setText("Features successful extracted!")

            dimensions = range(self.X.shape[1])
            attributes = [
                ContinuousVariable.make(
                    'Feature {:d}'.format(d)) for d in dimensions]

            if self.data.Y != []:
                Y = DiscreteVariable.make(
                    "Target class",
                    values=self.data.domain.class_var.values,
                    ordered=True)
            else:
                Y = None

            self.domain = Domain(
                attributes=attributes,
                class_vars=Y,
                metas=self.data.domain.metas)
            orange_table = Table(
                self.domain,
                self.X,
                self.data.Y,
                self.data.metas)

            self.send("Extracted features", orange_table)

        if error:
            self.info.setStyleSheet(error_red)
            self.info.setText("An error occurred:\n{}".format(error))
            return
