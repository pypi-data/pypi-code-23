from PyQt5 import QtWidgets
from sklearn.linear_model import ElasticNet
from sklearn.linear_model.coordinate_descent import ElasticNetCV

from point_spectra_gui.ui.ElasticNet import Ui_Form
from point_spectra_gui.util.Modules import Modules


class Ui_Form(Ui_Form, ElasticNet, ElasticNetCV, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        self.connectWidgets()

    def get_widget(self):
        return self.groupBox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        en = ElasticNet()

        self.alpha_text.setText(str(en.alpha))
        self.enl1_ratioDoubleSpinBox.setValue(en.l1_ratio)
        self.enfit_interceptCheckBox.setChecked(en.fit_intercept)
        self.ennormalizeCheckBox.setChecked(en.normalize)
        self.enmax_iterSpinBox.setValue(en.max_iter)
        self.entolDoubleSpinBox.setValue(en.tol)
        self.enpositiveCheckBox.setChecked(en.positive)
        self.setComboBox(self.enselectionComboBox, ['cyclic', 'random'])
        self.defaultComboItem(self.enselectionComboBox, en.selection)


    def run(self):
        params = {
                'alpha': float(self.alpha_text.text()),
                'l1_ratio': self.enl1_ratioDoubleSpinBox.value(),
                'fit_intercept': self.enfit_interceptCheckBox.isChecked(),
                'normalize': self.ennormalizeCheckBox.isChecked(),
                'precompute': True,
                'max_iter': self.enmax_iterSpinBox.value(),
                'copy_X': True,
                'tol': self.entolDoubleSpinBox.value(),
                'warm_start': True,
                'positive': self.enpositiveCheckBox.isChecked(),
                'selection': 'random'
                }
        return params, self.getChangedValues(params, ElasticNet())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
