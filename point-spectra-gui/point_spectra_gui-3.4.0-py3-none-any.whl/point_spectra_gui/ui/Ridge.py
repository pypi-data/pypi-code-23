# -*- coding: utf-8 -*-

# Automatically generated - don't edit.
# Use `python setup.py build_ui` to update it.

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Ridge = QtWidgets.QGroupBox(self.groupBox)
        self.Ridge.setEnabled(True)
        self.Ridge.setObjectName("Ridge")
        self.formLayout_2 = QtWidgets.QFormLayout(self.Ridge)
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.alphaLabel = QtWidgets.QLabel(self.Ridge)
        self.alphaLabel.setObjectName("alphaLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.alphaLabel)
        self.alphaDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.Ridge)
        self.alphaDoubleSpinBox.setProperty("value", 1.0)
        self.alphaDoubleSpinBox.setObjectName("alphaDoubleSpinBox")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.alphaDoubleSpinBox)
        self.fitInterceptLabel = QtWidgets.QLabel(self.Ridge)
        self.fitInterceptLabel.setObjectName("fitInterceptLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.fitInterceptLabel)
        self.fitInterceptCheckBox = QtWidgets.QCheckBox(self.Ridge)
        self.fitInterceptCheckBox.setChecked(True)
        self.fitInterceptCheckBox.setObjectName("fitInterceptCheckBox")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.fitInterceptCheckBox)
        self.maxNumOfIterationsLabel = QtWidgets.QLabel(self.Ridge)
        self.maxNumOfIterationsLabel.setObjectName("maxNumOfIterationsLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.maxNumOfIterationsLabel)
        self.maxNumOfIterationslineEdit = QtWidgets.QLineEdit(self.Ridge)
        self.maxNumOfIterationslineEdit.setObjectName("maxNumOfIterationslineEdit")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.maxNumOfIterationslineEdit)
        self.normalizeLabel = QtWidgets.QLabel(self.Ridge)
        self.normalizeLabel.setObjectName("normalizeLabel")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.normalizeLabel)
        self.normalizeCheckBox = QtWidgets.QCheckBox(self.Ridge)
        self.normalizeCheckBox.setObjectName("normalizeCheckBox")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.normalizeCheckBox)
        self.toleranceLabel = QtWidgets.QLabel(self.Ridge)
        self.toleranceLabel.setObjectName("toleranceLabel")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.toleranceLabel)
        self.toleranceDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.Ridge)
        self.toleranceDoubleSpinBox.setObjectName("toleranceDoubleSpinBox")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.toleranceDoubleSpinBox)
        self.horizontalLayout.addWidget(self.Ridge)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.formGroupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.formGroupBox_2.setObjectName("formGroupBox_2")
        self.formLayout_5 = QtWidgets.QFormLayout(self.formGroupBox_2)
        self.formLayout_5.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_5.setObjectName("formLayout_5")
        self.verticalLayout.addWidget(self.formGroupBox_2)
        self.verticalLayout_2.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.Ridge.setTitle(("Ridge"))
        self.alphaLabel.setText(("Alpha"))
        self.alphaDoubleSpinBox.setToolTip(_translate("Form", "Regularization strength; must be a positive float. Regularization\n"
"improves the conditioning of the problem and reduces the variance of\n"
"the estimates. Larger values specify stronger regularization. Alpha\n"
"corresponds to C^-1 in other linear models such as LogisticRegression\n"
"or LinearSVC. If an array is passed, penalties are assumed to be specific\n"
"to the targets. Hence they must correspond in number.\n"
""))
        self.alphaDoubleSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html"))
        self.fitInterceptLabel.setText(("Fit Intercept"))
        self.fitInterceptCheckBox.setToolTip(_translate("Form", "Whether to calculate the intercept for this model. If set to false,\n"
"no intercept will be used in calculations (e.g. data is expected to\n"
"be already centered)."))
        self.fitInterceptCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html"))
        self.maxNumOfIterationsLabel.setText(("Max # of Iterations"))
        self.maxNumOfIterationslineEdit.setToolTip(_translate("Form", "Maximum number of iterations for conjugate gradient solver. For\n"
"\'sparse_cg\' and \'lsqr\' solvers, the default value is determined by\n"
"scipy.sparse.linalg. For \'sag\' solver, the default value is 1000.\n"
""))
        self.maxNumOfIterationslineEdit.setText(("None"))
        self.normalizeLabel.setText(("Normalize"))
        self.normalizeCheckBox.setToolTip(_translate("Form", "This parameter is ignored when fit_intercept is set to False. If True,\n"
"the regressors X will be normalized before regression by subtracting\n"
"the mean and dividing by the l2-norm. If you wish to standardize,\n"
"please use sklearn.preprocessing.StandardScaler before calling fit on\n"
"an estimator with normalize=False."))
        self.normalizeCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html"))
        self.toleranceLabel.setText(("Tolerance"))
        self.toleranceDoubleSpinBox.setToolTip(("Precision of the solution."))
        self.toleranceDoubleSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

