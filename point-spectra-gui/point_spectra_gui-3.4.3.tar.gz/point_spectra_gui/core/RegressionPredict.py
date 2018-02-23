from PyQt5 import QtWidgets

from point_spectra_gui.ui.RegressionPredict import Ui_Form
from point_spectra_gui.util.Modules import Modules


class RegressionPredict(Ui_Form, Modules):
    count = -1

    def __init__(self):
        RegressionPredict.count += 1
        self.curr_count = RegressionPredict.count

    def delete(self):
        try:
            RegressionPredict.count -= 1
            del self.modelkeys[-1]
        except IndexError:
            pass

    def setupUi(self, Form):
        super().setupUi(Form)
        Modules.setupUi(self, Form)

    def get_widget(self):
        return self.formGroupBox

    def connectWidgets(self):
        self.setListWidget(self.chooseDataListWidget, self.datakeys)
        self.setComboBox(self.chooseModelComboBox, self.modelkeys)

    def setup(self):
        datakeys = [str(i.text()) for i in self.chooseDataListWidget.selectedItems()]
        modelkey = self.chooseModelComboBox.currentText()
        try:
            for datakey in datakeys:
                data_tmp = self.data[datakey].df[self.model_xvars[modelkey]]
                data_tmp.fillna(value=0, inplace=True)
                prediction = self.models[modelkey].predict(data_tmp)
                predictname = ('predict', modelkey + ' - ' + datakey + ' - Predict')
                self.data[datakey].df[predictname] = prediction
        except Exception as e:
            print(e)

    def run(self):
        datakeys = [str(i.text()) for i in self.chooseDataListWidget.selectedItems()]
        modelkey = self.chooseModelComboBox.currentText()
        try:
            for datakey in datakeys:
                data_tmp = self.data[datakey].df[self.model_xvars[modelkey]]
                data_tmp.fillna(value=0, inplace=True)
                prediction = self.models[modelkey].predict(data_tmp)
                predictname = ('predict', modelkey + ' - ' + datakey + ' - Predict')
                self.data[datakey].df[predictname] = prediction
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    Form = QtWidgets.QWidget()
    ui = RegressionPredict()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
