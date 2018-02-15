import re
from sys import argv, exit
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from queue import Queue, Empty
from .ui.MainWindow import Ui_MainWindow
from .core import Resizer
from .utils import start_thread


class Resizer_GUI(Resizer):
    def __init__(self, input_dir, output_dir, size, quality):
        super().__init__(input_dir, output_dir, size, quality)
        self.message_queue = Queue()
        self.listener = None
        self.listener_thread = None

    def show_progress(self, src, percent, count, total_count):
        data = {'count': count,
                'total_count': total_count,
                'percent': percent,
                'src': src}
        self.message_queue.put(data)

    def run(self):
        execution_time = super().run()
        msg_time = {'execution_time': execution_time}
        self.message_queue.put(msg_time)
        self.listener.stop()
        self.listener_thread.quit()


class GuiReceiver(QObject):
    gotMessage = pyqtSignal(dict)
    finished = pyqtSignal(int)

    def __init__(self, message_queue):
        QObject.__init__(self)
        self.message_queue = message_queue
        self.is_alive = False

    def poll(self):
        self.is_alive = True
        while self.is_alive:
            try:
                msg = self.message_queue.get(timeout=1)
                self.gotMessage.emit(msg)
            except Empty:
                pass
        self.finished.emit(0)

    def stop(self):
        self.is_alive = False


class Resizer_Qt5_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.resizer = None
        self.resizer_thread = None
        # UI
        self.initUI()

    def initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton_Source.clicked.connect(self.getSourceDir)
        self.ui.pushButton_Destination.clicked.connect(self.getDestinationDir)
        self.ui.pushButton_Start.clicked.connect(self.start)
        self.ui.comboBox_Preset.currentIndexChanged.connect(self.preset)
        self.ui.comboBox_Preset.setCurrentIndex(1)

    def start(self):
        self.ui.plainTextEdit_Output.clear()
        src = self.ui.lineEdit_Source.text()
        dst = self.ui.lineEdit_Destination.text()
        width = self.ui.spinBox_Width.text()
        height = self.ui.spinBox_Height.text()
        size = (int(width), int(height))
        quality = int(self.ui.spinBox_Quality.text())
        self.run(src, dst, size, quality)

    def run(self, src, dst, size, quality):
        resizer = Resizer_GUI(src, dst, size, quality)

        listener = GuiReceiver(resizer.message_queue)
        listener.gotMessage.connect(self.show_progress)
        listener_thread = QThread()
        listener.moveToThread(listener_thread)
        listener_thread.started.connect(listener.poll)
        listener_thread.start()

        resizer.listener = listener
        resizer.listener_thread = listener_thread
        resizer_thread = start_thread(resizer.run)

        self.resizer = resizer
        self.resizer_thread = resizer_thread

    def show_progress(self, data):
        try:
            if 'percent' in data:
                self.ui.progressBar.setValue(int(data['percent']))
                msg = '{}/{} ({}%) : {}'.format(data['count'], data['total_count'], data['percent'], data['src'])
                self.ui.plainTextEdit_Output.insertPlainText('{}\n'.format(msg))
                self.ui.plainTextEdit_Output.moveCursor(QtGui.QTextCursor.End)
            else:
                msg = 'Время выполнения: {} секунд'.format(data['execution_time'])
                self.ui.statusbar.showMessage(msg)
        except Exception as e:
            print(e)

    def preset(self):
        text = self.ui.comboBox_Preset.currentText()
        preset = re.findall('^(\d+)x(\d+)_(\d+) - .+', text)[0]
        width, height, quality = (int(x) for x in preset)
        self.ui.spinBox_Width.setValue(width)
        self.ui.spinBox_Height.setValue(height)
        self.ui.spinBox_Quality.setValue(quality)

    def getSourceDir(self):
        src = self.browseDir()
        self.ui.lineEdit_Source.setText(src)
        if not self.ui.lineEdit_Destination.text():
            self.ui.lineEdit_Destination.setText(src + '_CONVERTED')

    def getDestinationDir(self):
        self.ui.lineEdit_Destination.setText(self.browseDir())

    def browseDir(self):
        return QtWidgets.QFileDialog.getExistingDirectory(self, 'Выберите каталог', '/home')


def main():
    app = QtWidgets.QApplication(argv)
    window = Resizer_Qt5_Window()
    window.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()