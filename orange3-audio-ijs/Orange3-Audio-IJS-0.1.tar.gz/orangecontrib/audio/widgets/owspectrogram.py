"""
Spectrogram
-----------

A widget for spectrogram visualization
"""
from AnyQt.QtCore import Qt, QEvent, QRectF, QSize

from PyQt4 import QtGui
import Orange.data
from Orange.widgets import widget, gui, settings

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from PyQt4.QtGui import QListWidget, QIcon, QPixmap
from scipy.io.wavfile import read
import os

scale = [
    "default",
    "linear",
    "dB"
]
mode = [
    "default",
    "psd",
    "magnitude",
    "angle",
    "phase"
]
class OWSpectrogram(widget.OWWidget):
    name = "Spectrogram"
    description = "Spectrogram visualization"
    icon = "icons/spectogram.png"
    priority = 6
    inputs = [("Data", Orange.data.Table, "set_data")]

    categories_settings = settings.Setting([])
    file_names_settings = settings.Setting([])

    nfft = settings.Setting(256)
    noverlap = settings.Setting(128)
    scale_id = settings.Setting(0)
    mode_id = settings.Setting(0)

    def __init__(self):
        print("to je tale ja")
        super().__init__()
        self.stats = []
        self.dataset = None
        self.categories = []
        self.file_names = []
        self.tmp_file_names = []

        gui.listBox(self.controlArea, self, 'categories_settings',
                   labels='categories',
                   box='Choose category',
                   selectionMode=QListWidget.ExtendedSelection,
                   callback=self.category_changed)

        gui.listBox(self.controlArea, self, 'file_names_settings',
                   labels='file_names',
                   box='File names',
                   selectionMode=QListWidget.ExtendedSelection,
                   callback=self.file_changed)

        parameters_box = gui.widgetBox(self.controlArea, 'Parameters')

        self.nfft_spin = gui.spin(
            parameters_box, self, "nfft", minv=1, maxv=10000, controlWidth=80,
            alignment=Qt.AlignRight, label="NFFT: ")
        self.noverlap_spin = gui.spin(
            parameters_box, self, "noverlap", minv=1, maxv=10000, controlWidth=80,
            alignment=Qt.AlignRight, label="Noverlap: ")
        self.scale_combo = gui.comboBox(parameters_box, self, "scale_id",orientation=Qt.Horizontal,
                                                 label="Scale type: ",
                                                 items=[m for m in scale]
                                                 )
        self.mode_combo = gui.comboBox(parameters_box, self, "mode_id",orientation=Qt.Horizontal,
                                        label="Mode type: ",
                                        items=[m for m in mode]
                                        )

        self.export_png_button = gui.button(self.controlArea, self, "Export to png",
                                            callback=lambda: self.export_to_png())

        self.figure = plt.figure()
        self.figure.patch.set_facecolor('white')

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(100)

        gui.vBox(self.mainArea, addSpace=True, sizePolicy=policy)

        self.mainArea.layout().addWidget(self.toolbar)
        self.mainArea.layout().addWidget(self.canvas)

        self.mainArea.setMinimumWidth(600)



    def set_data(self, dataset):
        """
        Set data from input

        :param dataset: input data
        :return: Void
        """

        self.reset_all_data()

        if dataset is not None:
            self.dataset = dataset

        if dataset:
            self.file_icon = QIcon(QPixmap("/home/borut/Downloads/index.jpeg"))

            if self.dataset.Y != []:
                self.file_names = [(str(d.get_class()) + os.sep + d.metas[0], self.file_icon) for d in dataset]
                self.file_names_settings = self.file_names[0]
                self.category_icon = QIcon(QPixmap("/home/borut/Downloads/Tag-512.png"))
                self.categories = [(var, self.category_icon) for var in self.dataset.domain.class_var.values]
                self.categories_settings = self.categories[0]

            else:
                self.file_names = [(d.metas[0], self.file_icon) for d in dataset]
                self.file_names_settings = self.file_names[0]
                self.category_icon = QIcon(QPixmap("/home/borut/Downloads/Tag-512.png"))
                self.categories = []

            self.plot(self.dataset.metas[0][1])


    def reset_all_data(self):
        """
        Reset file names and categories

        :return: Void
        """
        self.file_names = []
        self.categories = []

    def file_changed(self):
        """
        Refresh spectrogram when file change

        :return: Void
        """

        if self.file_names_settings != []:
            selectedFile = self.file_names[self.file_names_settings[-1]][0]
            split_selectedFile = selectedFile.split(os.sep)

            if len(split_selectedFile) == 1:
                for d in self.dataset:
                    if d.metas[0] == split_selectedFile[0]:
                        self.plot(d.metas[1])

            else:
                category = selectedFile.split(os.sep)[0]
                fileName = selectedFile.split(os.sep)[1]
                for d in self.dataset:
                    if d.get_class() == category and d.metas[0] == fileName:
                        self.plot(d.metas[1])



    def category_changed(self):
        """
        Refresh file names when category change

        :return: Void
        """

        category_list = [self.categories [x][0] for x in self.categories_settings]

        tmp = []
        for x in self.dataset:
            for i in category_list:
                if x.get_class() == i:
                    tmp.append((str(x.get_class()) + os.sep + x.metas[0], self.file_icon))
        self.file_names = tmp

    def plot(self, dir):
        """
        Plot spectrogram

        :param dir: name of file directory
        :return: Void
        """

        if dir == None:
            return

        self.figure.clf()
        framerate, data = read(dir)
        ax1 = plt.subplot(111)
        if data.ndim == 1:
            Pxx, freqs, bins, im = plt.specgram(data,
                                                NFFT=self.nfft, noverlap=self.noverlap,
                                                Fs=framerate, mode=self.mode_combo.currentText(),
                                                scale=self.scale_combo.currentText(), aspect="auto")
        else:
            Pxx, freqs, bins, im = plt.specgram(data[:,0],
                                                NFFT=self.nfft, noverlap=self.noverlap,
                                                Fs=framerate, mode=self.mode_combo.currentText(),
                                                scale=self.scale_combo.currentText(), aspect="auto")
        ax1.autoscale_view('tight')
        plt.colorbar(im).set_label('Intensity [dB]')
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (hz)")


        self.canvas.draw()

    def export_to_png(self):
        """
        Selected spectrograms is saved to local file system

        :return: Void
        """

        for i in self.file_names_settings:
            selectedFile = self.file_names[i][0]
            category = selectedFile.split(os.sep)[0]
            fileName = selectedFile.split(os.sep)[1]

            for d in self.dataset:
                if d.get_class() == category and d.metas[0] == fileName:
                    dir = d.metas[1]

            framerate, data = read(dir)

            self.figure.clf()
            Pxx, freqs, bins, im = plt.specgram(data[:,0],
                                            NFFT=self.nfft, noverlap=self.noverlap,
                                            Fs=framerate, mode=self.mode_combo.currentText(),
                                            scale=self.scale_combo.currentText())

            plt.colorbar(im).set_label('Intensity [dB]')
            plt.xlabel("Time (s)")
            plt.ylabel("Frequency (hz)")

            path = "".join(f + os.sep for f in dir.split(os.sep)[:-1])
            plt.savefig(path + fileName + ".png")
