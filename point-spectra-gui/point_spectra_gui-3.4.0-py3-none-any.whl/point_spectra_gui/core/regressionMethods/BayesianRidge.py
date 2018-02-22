from PyQt5 import QtWidgets
from point_spectra_gui.ui.BayesianRidge import Ui_Form
from point_spectra_gui.util.Modules import Modules
from sklearn.linear_model import BayesianRidge


class Ui_Form(Ui_Form, BayesianRidge, Modules):
    def setupUi(self, Form):
        super().setupUi(Form)
        self.checkMinAndMax()
        self.connectWidgets()

    def get_widget(self):
        return self.formGroupBox

    def setHidden(self, bool):
        self.get_widget().setHidden(bool)

    def connectWidgets(self):
        self.numOfIterationsSpinBox.setValue(self.n_iter)
        self.toleranceDoubleSpinBox.setValue(self.tol)
        self.alpha1DoubleSpinBox.setValue(self.alpha_1)
        self.alpha2DoubleSpinBox.setValue(self.alpha_2)
        self.lambdaDoubleSpinBox.setValue(self.lambda_1)
        self.lambdaDoubleSpinBox.setValue(self.lambda_2)
        self.computerScoreCheckBox.setChecked(self.compute_score)
        self.fitInterceptCheckBox.setChecked(self.fit_intercept)
        self.normalizeCheckBox.setChecked(self.normalize)

    def run(self):
        params = {'n_iter': self.numOfIterationsSpinBox.value(),
                  'tol': self.toleranceDoubleSpinBox.value(),
                  'alpha_1': self.alpha1DoubleSpinBox.value(),
                  'alpha_2': self.alpha2DoubleSpinBox.value(),
                  'lambda_1': self.lambdaDoubleSpinBox.value(),
                  'lambda_2': self.lambdaDoubleSpinBox.value(),
                  'compute_score': self.computerScoreCheckBox.isChecked(),
                  'fit_intercept': self.fitInterceptCheckBox.isChecked(),
                  'normalize': self.normalizeCheckBox.isChecked(),
                  }
        return params, self.getChangedValues(params, BayesianRidge())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
