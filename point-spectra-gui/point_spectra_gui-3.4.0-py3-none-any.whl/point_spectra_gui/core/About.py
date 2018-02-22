from PyQt5 import QtWidgets

from point_spectra_gui.__init__ import __version__
from point_spectra_gui.ui.About import Ui_Form


class About(QtWidgets.QWidget, Ui_Form):
    """
    Display the version for the User. Good for debugging purposes
    """

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.versionLabel.setText("Version " + __version__)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    form = About()
    form.show()
    sys.exit(app.exec_())

