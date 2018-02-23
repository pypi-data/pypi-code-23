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
        self.formGroupBox = QtWidgets.QGroupBox(Form)
        self.formGroupBox.setObjectName("formGroupBox")
        self.formLayout = QtWidgets.QFormLayout(self.formGroupBox)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.alphaLabel = QtWidgets.QLabel(self.formGroupBox)
        self.alphaLabel.setObjectName("alphaLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.alphaLabel)
        self.alpha_text = QtWidgets.QLineEdit(self.formGroupBox)
        self.alpha_text.setObjectName("alpha_text")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.alpha_text)
        self.fit_interceptLabel = QtWidgets.QLabel(self.formGroupBox)
        self.fit_interceptLabel.setObjectName("fit_interceptLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.fit_interceptLabel)
        self.fit_interceptCheckBox = QtWidgets.QCheckBox(self.formGroupBox)
        self.fit_interceptCheckBox.setObjectName("fit_interceptCheckBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.fit_interceptCheckBox)
        self.normalizeLabel = QtWidgets.QLabel(self.formGroupBox)
        self.normalizeLabel.setObjectName("normalizeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.normalizeLabel)
        self.normalizeCheckBox = QtWidgets.QCheckBox(self.formGroupBox)
        self.normalizeCheckBox.setObjectName("normalizeCheckBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.normalizeCheckBox)
        self.max_iterLabel = QtWidgets.QLabel(self.formGroupBox)
        self.max_iterLabel.setObjectName("max_iterLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.max_iterLabel)
        self.max_iterSpinBox = QtWidgets.QSpinBox(self.formGroupBox)
        self.max_iterSpinBox.setObjectName("max_iterSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.max_iterSpinBox)
        self.positiveLabel = QtWidgets.QLabel(self.formGroupBox)
        self.positiveLabel.setObjectName("positiveLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.positiveLabel)
        self.positiveCheckBox = QtWidgets.QCheckBox(self.formGroupBox)
        self.positiveCheckBox.setObjectName("positiveCheckBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.positiveCheckBox)
        self.verticalLayout.addWidget(self.formGroupBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(("Form"))
        self.formGroupBox.setTitle(("LASSO LARS"))
        self.alphaLabel.setText(("Alpha"))
        self.fit_interceptLabel.setText(("Fit Intercept"))
        self.fit_interceptCheckBox.setToolTip(_translate("Form", "whether to calculate the intercept for this model. If set to false,\n"
"no intercept will be used in calculations (e.g. data is expected to\n"
"be already centered)."))
        self.fit_interceptCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoLars.html"))
        self.normalizeLabel.setText(("Normalize"))
        self.normalizeCheckBox.setToolTip(_translate("Form", "This parameter is ignored when fit_intercept is set to False. If True,\n"
"the regressors X will be normalized before regression by subtracting\n"
"the mean and dividing by the l2-norm. If you wish to standardize,\n"
"please use sklearn.preprocessing.StandardScaler before calling fit\n"
"on an estimator with normalize=False."))
        self.normalizeCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoLars.html"))
        self.max_iterLabel.setText(("Max # of iterations"))
        self.max_iterSpinBox.setToolTip(("Maximum number of iterations to perform."))
        self.max_iterSpinBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoLars.html"))
        self.positiveLabel.setText(("Force positive coefficients"))
        self.positiveCheckBox.setToolTip(_translate("Form", "Restrict coefficients to be >= 0. Be aware that you might want to\n"
"remove fit_intercept which is set True by default. Under the positive\n"
"restriction the model coefficients will not converge to the\n"
"ordinary-least-squares solution for small values of alpha. Only\n"
"coefficients up to the smallest alpha value\n"
"(alphas_[alphas_ > 0.].min() when fit_path=True) reached by the\n"
"stepwise Lars-Lasso algorithm are typically in congruence with the\n"
"solution of the coordinate descent Lasso estimator."))
        self.positiveCheckBox.setWhatsThis(("http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoLars.html"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

