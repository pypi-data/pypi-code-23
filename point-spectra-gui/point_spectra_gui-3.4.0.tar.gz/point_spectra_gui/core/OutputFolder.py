from PyQt5 import QtWidgets

from point_spectra_gui.ui.OutputFolder import Ui_Form
from point_spectra_gui.util.Modules import Modules


class OutputFolder(Ui_Form, Modules):
    """
    This is the `outpath` module. It can designate where data goes after processing
    """

    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupBox

    def on_outPutLocationButton_clicked(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Output Directory", '.')
        self.folderNameLineEdit.setText(filename)
        if self.folderNameLineEdit.text() == "":
            self.folderNameLineEdit.setText("*/")

    def connectWidgets(self):
        self.pushButton.clicked.connect(lambda: self.on_outPutLocationButton_clicked())

    def setup(self):
        pass

    def run(self):
        outpath = self.folderNameLineEdit.text()
        try:
            Modules.outpath = outpath
            print("Output path folder has been set to " + outpath)
        except Exception as e:
            print("Error: {}; using default outpath: {}".format(e, Modules.outpath))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = OutputFolder()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
