"""
Audio Player
-----------

A widget for playing audio recordings.
"""

import Orange.data
from Orange.widgets import widget, gui, settings
from PyQt4 import QtCore, QtGui
import sys

error_red = 'QWidget { color:#f9221b;}'
success_green = 'QWidget { color:#42f442;}'
Phonon_support = True

try:
    from PyQt4.phonon import Phonon
except ImportError:
    Phonon_support = False

class OWAudioPlayer(widget.OWWidget):
    name = "Audio Player"
    description = "Plays audio recordings"
    priority = 7
    icon = "icons/audio_player.png"

    inputs = [("Data", Orange.data.Table, "set_data")]

    file_id = settings.Setting(0)

    want_main_area = False

    data = None

    def __init__(self):
        super().__init__()

        info_box = gui.widgetBox(self.controlArea, "Info")

        if not Phonon_support:
            self.info = gui.widgetLabel(
                info_box, "Your Qt installation does not have Phonon support.")
            return

        self.info = gui.widgetLabel(
            info_box, 'No data on input yet, waiting to get something.')

        self.files_combo = gui.comboBox(self.controlArea, self, "file_id",
                                        box="File names"
                                        )

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(1000)

        self.mediaObject.tick.connect(self.tick)
        self.mediaObject.stateChanged.connect(self.stateChanged)
        self.mediaObject.currentSourceChanged.connect(self.sourceChanged)

        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.setupActions()
        self.setupMusicGui()
        self.timeLcd.display("00:00")

        self.files_combo.activated.connect(self.handleFilesCombo)
        self.sources = []

    def set_data(self, dataset):
        """
        Set data from input

        :param dataset: input data
        :return: Void
        """

        if dataset is not None:
            self.info.setText('%d instances in input data set' % len(dataset))
            self.data = dataset
            print(self.data.metas[:, 0])
            if self.data.Y != []:
                self.file_names = [str(x) + "/" + str(y) for x,
                               y in zip([i.get_class() for i in self.data],
                                    self.data.metas[:,0])]
            else:
                self.file_names = self.data.metas[:,0]

            self.files_combo.addItems(self.file_names)

            for string in self.data.metas[:, 1]:
                self.sources.append(Phonon.MediaSource(string))
            if self.sources:
                self.metaInformationResolver.setCurrentSource(self.sources[0])
        else:
            self.info.setText(
                'No data on input yet, waiting to get something.')

    def handleFilesCombo(self):
        """
        Handle changing files from audio records list

        :return:Void
        """

        if self.mediaObject.state() == Phonon.PlayingState:
            self.mediaObject.stop()
        else:
            path = self.data.metas[self.files_combo.currentIndex()][1]
            if path:
                self.mediaObject.setCurrentSource(Phonon.MediaSource(path))
                self.mediaObject.play()

    def stateChanged(self, newState):
        """
        Handle buttons for play, pause and stop

        :param newState: new state (play, pause, stop)
        :return: Void
        """

        if newState == Phonon.ErrorState:
            if self.mediaObject.errorType() == Phonon.FatalError:
                QtGui.QMessageBox.warning(self, "Fatal Error",
                                          self.mediaObject.errorString())
            else:
                QtGui.QMessageBox.warning(self, "Error",
                                          self.mediaObject.errorString())

        elif newState == Phonon.PlayingState:
            self.playAction.setEnabled(False)
            self.pauseAction.setEnabled(True)
            self.stopAction.setEnabled(True)

        elif newState == Phonon.StoppedState:
            self.stopAction.setEnabled(False)
            self.playAction.setEnabled(True)
            self.pauseAction.setEnabled(False)
            self.timeLcd.display("00:00")

        elif newState == Phonon.PausedState:
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(True)
            self.playAction.setEnabled(True)

    def tick(self, time):
        """
        Signal which give the current position of the media object in the stream

        :param time: playing time in milliseconds
        :return: Void
        """

        displayTime = QtCore.QTime(0, (time / 60000) % 60, (time / 1000) % 60)
        self.timeLcd.display(displayTime.toString('mm:ss'))

    def sourceChanged(self):
        """
        Reset time when source change

        :return: None
        """
        self.timeLcd.display('00:00')

    def setupActions(self):
        """
        Define basics 3 actions:
            - Play
            - Pause
            - Stop

        :return: Void
        """

        self.playAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
            self, shortcut="Ctrl+P", enabled=False,
            triggered=self.mediaObject.play)

        self.pauseAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
            "Pause", self, shortcut="Ctrl+A", enabled=False,
            triggered=self.mediaObject.pause)

        self.stopAction = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
            self, shortcut="Ctrl+S", enabled=False,
            triggered=self.mediaObject.stop)

    def setupMusicGui(self):
        """
        Define all music GUI components

        :return: Void
        """

        # Define GUI components for 3 basics actions
        actionBar = QtGui.QToolBar()

        actionBar.addAction(self.playAction)
        actionBar.addAction(self.pauseAction)
        actionBar.addAction(self.stopAction)

        # Defining seek slider
        self.seekSlider = Phonon.SeekSlider(self)
        self.seekSlider.setMediaObject(self.mediaObject)

        # Defining palette and lcd time
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Light, QtCore.Qt.darkGray)

        self.timeLcd = QtGui.QLCDNumber()
        self.timeLcd.setPalette(palette)

        # Defining volume icon and slider
        volumeLabel = QtGui.QLabel()
        volumeLabel.setPixmap(QtGui.QPixmap('images/volume.png'))

        self.volumeSlider = Phonon.VolumeSlider(self)
        self.volumeSlider.setAudioOutput(self.audioOutput)
        self.volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                        QtGui.QSizePolicy.Maximum)

        # Defining seekerLayout which include seek slider and lcd time
        seekerLayout = QtGui.QHBoxLayout()
        seekerLayout.addWidget(self.seekSlider)
        seekerLayout.addWidget(self.timeLcd)

        # Defining playbackLayout which inlcude seekerLayout and volumeSlider
        # with icon
        playbackLayout = QtGui.QHBoxLayout()
        playbackLayout.addWidget(actionBar)
        playbackLayout.addStretch()
        playbackLayout.addWidget(volumeLabel)
        playbackLayout.addWidget(self.volumeSlider)

        # Defining mainLayout which include seekerLayout and playbackLayout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(seekerLayout)
        mainLayout.addLayout(playbackLayout)

        # Defining Player box which include mainLayout
        box = gui.widgetBox(self.controlArea, 'Player')
        box.layout().addLayout(mainLayout)
