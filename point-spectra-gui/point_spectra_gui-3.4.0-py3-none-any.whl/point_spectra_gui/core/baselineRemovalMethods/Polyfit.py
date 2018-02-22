from PyQt5 import QtWidgets
from libpysat.spectral.baseline_code.polyfit import PolyFit

from point_spectra_gui.ui.Polyfit import Ui_Form
from point_spectra_gui.util.Modules import Modules


class Ui_Form(Ui_Form, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.groupbox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        br = PolyFit()
        self.orderSpinBox.setValue(br.poly_order_)
        self.numOfStandardDeviationsSpinBox.setValue(br.stdv_)

    def run(self):
        methodParameters = {'poly_order_': self.orderSpinBox.value(),
                            'stdv_': self.numOfStandardDeviationsSpinBox.value(),
                            'max_iter_': self.maxNumOfIterationsSpinBox.value()}
        return methodParameters, self.getChangedValues(methodParameters, PolyFit())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
