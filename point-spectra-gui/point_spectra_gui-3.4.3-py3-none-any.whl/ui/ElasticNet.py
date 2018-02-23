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
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.ENLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.ENLayout.setObjectName("ENLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.elasticNetGroupBox = QtWidgets.QGroupBox(self.groupBox)
        self.elasticNetGroupBox.setObjectName("elasticNetGroupBox")
        self.ElasticNet = QtWidgets.QFormLayout(self.elasticNetGroupBox)
        self.ElasticNet.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.ElasticNet.setObjectName("ElasticNet")
        self.enalphaLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enalphaLabel.setObjectName("enalphaLabel")
        self.ElasticNet.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.enalphaLabel)
        self.alpha_text = QtWidgets.QLineEdit(self.elasticNetGroupBox)
        self.alpha_text.setObjectName("alpha_text")
        self.ElasticNet.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.alpha_text)
        self.enl1_ratioLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enl1_ratioLabel.setObjectName("enl1_ratioLabel")
        self.ElasticNet.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.enl1_ratioLabel)
        self.enl1_ratioDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.elasticNetGroupBox)
        self.enl1_ratioDoubleSpinBox.setObjectName("enl1_ratioDoubleSpinBox")
        self.ElasticNet.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.enl1_ratioDoubleSpinBox)
        self.enfit_interceptLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enfit_interceptLabel.setObjectName("enfit_interceptLabel")
        self.ElasticNet.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.enfit_interceptLabel)
        self.enfit_interceptCheckBox = QtWidgets.QCheckBox(self.elasticNetGroupBox)
        self.enfit_interceptCheckBox.setObjectName("enfit_interceptCheckBox")
        self.ElasticNet.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.enfit_interceptCheckBox)
        self.ennormalizeLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.ennormalizeLabel.setObjectName("ennormalizeLabel")
        self.ElasticNet.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.ennormalizeLabel)
        self.ennormalizeCheckBox = QtWidgets.QCheckBox(self.elasticNetGroupBox)
        self.ennormalizeCheckBox.setObjectName("ennormalizeCheckBox")
        self.ElasticNet.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.ennormalizeCheckBox)
        self.enmax_iterLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enmax_iterLabel.setObjectName("enmax_iterLabel")
        self.ElasticNet.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.enmax_iterLabel)
        self.enmax_iterSpinBox = QtWidgets.QSpinBox(self.elasticNetGroupBox)
        self.enmax_iterSpinBox.setObjectName("enmax_iterSpinBox")
        self.ElasticNet.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.enmax_iterSpinBox)
        self.entolLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.entolLabel.setObjectName("entolLabel")
        self.ElasticNet.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.entolLabel)
        self.entolDoubleSpinBox = QtWidgets.QDoubleSpinBox(self.elasticNetGroupBox)
        self.entolDoubleSpinBox.setObjectName("entolDoubleSpinBox")
        self.ElasticNet.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.entolDoubleSpinBox)
        self.enpositiveLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enpositiveLabel.setObjectName("enpositiveLabel")
        self.ElasticNet.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.enpositiveLabel)
        self.enpositiveCheckBox = QtWidgets.QCheckBox(self.elasticNetGroupBox)
        self.enpositiveCheckBox.setObjectName("enpositiveCheckBox")
        self.ElasticNet.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.enpositiveCheckBox)
        self.enselectionLabel = QtWidgets.QLabel(self.elasticNetGroupBox)
        self.enselectionLabel.setObjectName("enselectionLabel")
        self.ElasticNet.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.enselectionLabel)
        self.enselectionComboBox = QtWidgets.QComboBox(self.elasticNetGroupBox)
        self.enselectionComboBox.setObjectName("enselectionComboBox")
        self.enselectionComboBox.addItem("")
        self.enselectionComboBox.addItem("")
        self.ElasticNet.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.enselectionComboBox)
        self.horizontalLayout.addWidget(self.elasticNetGroupBox)
        self.ENLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.elasticNetGroupBox.setTitle(("Elastic Net"))
        self.enalphaLabel.setText(("Alpha"))
        self.enl1_ratioLabel.setText(("L1 Ratio"))
        self.enl1_ratioDoubleSpinBox.setToolTip(_translate("Form", "The ElasticNet mixing parameter, with 0 <= l1_ratio <= 1. For l1_ratio\n"
"= 0 the penalty is an L2 penalty. For l1_ratio = 1 it is an L1 penalty.\n"
"For 0 < l1_ratio < 1, the penalty is a combination of L1 and L2."))
        self.enl1_ratioDoubleSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.enfit_interceptLabel.setText(("Fit Intercept"))
        self.enfit_interceptCheckBox.setToolTip(_translate("Form", "Whether the intercept should be estimated or not. If False, the data\n"
"is assumed to be already centered."))
        self.enfit_interceptCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.ennormalizeLabel.setText(("Normalize"))
        self.ennormalizeCheckBox.setToolTip(_translate("Form", "This parameter is ignored when fit_intercept is set to False. If True,\n"
"the regressors X will be normalized before regression by subtracting\n"
"the mean and dividing by the l2-norm. If you wish to standardize,\n"
"please use sklearn.preprocessing. StandardScaler before calling fit on\n"
"an estimator with normalize=False."))
        self.ennormalizeCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.enmax_iterLabel.setText(("Max # of iterations"))
        self.enmax_iterSpinBox.setToolTip(("The maximum number of iterations"))
        self.enmax_iterSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.entolLabel.setText(("Tolerance"))
        self.entolDoubleSpinBox.setToolTip(("The tolerance for the optimization:"))
        self.entolDoubleSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.enpositiveLabel.setText(("Positive"))
        self.enpositiveCheckBox.setToolTip(("When set to True, forces the coefficients to be positive."))
        self.enpositiveCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.enselectionLabel.setText(("Selection"))
        self.enselectionComboBox.setToolTip(_translate("Form", "If set to \'random\', a random coefficient is updated every iteration\n"
"rather than looping over features sequentially by default. This\n"
"(setting to \'random\') often leads to significantly faster convergence\n"
"especially when tol is higher than 1e-4."))
        self.enselectionComboBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html"))
        self.enselectionComboBox.setItemText(0, ("cyclic"))
        self.enselectionComboBox.setItemText(1, ("random"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

