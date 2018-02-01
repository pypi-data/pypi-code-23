from AnyQt.QtWidgets import QDoubleSpinBox, QApplication, QPushButton, QLineEdit
from Orange.widgets.widget import OWWidget
from Orange.widgets.gui import lineEdit



from Orange.widgets.gui import widgetBox, connectControl, miscellanea, CallFrontLineEdit, getdeepattr, widgetLabel
from AnyQt.QtCore import Qt


class TestWidget(OWWidget):

    def __init__(self):
        le = QLineEdit(self)
        le.setPlaceholderText("Ordinary QLineEdit")
        self.controlArea.layout().addWidget(le)
        spin = QDoubleSpinBox(minimum=0, maximum=1, singleStep=0.5)
        self.content = ""
        self.controlArea.layout().addWidget(spin)
        #leorange = lineEdit(self.controlArea, self, "content", callback=lambda: print("confirmed"))
        #leorange.setPlaceholderText("Orange Lineedit")
        lenew = lineEdit2(self.controlArea, self, "content", callback=lambda: print("confirmed2"))
        lenew.setPlaceholderText("New lineedit")
        b = QPushButton("Some button")
        b.setAutoDefault(False)
        self.controlArea.layout().addWidget(b)
        b.clicked.connect(lambda: print("Button activated"))


if __name__ == "__main__":
    app = QApplication([])
    w = TestWidget()
    w.show()
    w.raise_()
    r = app.exec_()
    w.onDeleteWidget()
