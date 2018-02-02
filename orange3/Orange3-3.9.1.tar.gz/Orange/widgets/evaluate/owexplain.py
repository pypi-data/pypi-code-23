from AnyQt.QtCore import Qt, QItemSelection, QItemSelectionModel, pyqtSlot
from AnyQt.QtWidgets import QApplication

from Orange.base import Model
from Orange.data import Table
from Orange.evaluation.interpret import LimeTabular
from Orange.widgets import widget, gui, settings


EMPTY_HTML = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
html, body {margin:0px;padding:0px;width:100%;height:100%;}
span:hover {color:OrangeRed !important}
span.selected {color:red !important}
</style>
</head>
<body id="canvas"></body>
</html>
"""


class OWExplain(widget.OWWidget):
    name = "LIME"
    priority = 2000
    icon = "icons/Predictions.svg"
    inputs = [("Model", Model, "set_model"),
              ("Training data", Table, "set_train"),
              ("Data", Table, "set_data")]

    graph_name = 'webview'

    autocommit = settings.Setting(True)
    discretize = settings.Setting(True)

    def __init__(self):
        super().__init__()
        self.model = None
        self.train = None
        self.data = None
        self.lime = None

        self.webview = gui.WebviewWidget(self.mainArea, self, debug=False)
        self.webview.setHtml(EMPTY_HTML)
        self.mainArea.layout().addWidget(self.webview)
        box = gui.widgetBox(self.controlArea, 'Info')
        self.info = gui.label(box, self, 'Model: Logistic Regression')
        box = gui.widgetBox(self.controlArea, 'Preferences')
        gui.checkBox(box, self, 'discretize', 'Discretize continuous', callback=self.disc_changed)
        gui.rubber(self.controlArea)

        self.apply_button = gui.auto_commit(
            self.controlArea, self, "autocommit", "&Commit") #, box=False)

    def set_model(self, model):
        self.model = model
        #self.info.setText('Model: ' + getattr(model, 'name', ''))
        self.lime = None

    def set_train(self, train):
        self.train = train
        self.lime = None

    def set_data(self, data):
        self.data = data

    def disc_changed(self):
        self.lime = None
        self.commit()

    def handleNewSignals(self):
        self.commit()

    def commit(self):
        if not (self.model and self.train and self.data
                and self.train.domain == self.data.domain
                and len(self.data) > 0):
            self.webview.setHtml(EMPTY_HTML)
            return
        if not self.lime:
            self.lime = LimeTabular(self.train, self.model, discretize_continuous=self.discretize)
        self.lime(self.data[0])
        self.webview.setHtml(open('/tmp/explanation.html').read())

    def send_report(self):
        self.report_plot()

    """
    def _new_webview(self):
        if self.webview:
            self.mainArea.layout().removeWidget(self.webview)
        self.webview = gui.WebviewWidget(self.mainArea, self, debug=False)
        self.webview.setHtml(EMPTY_HTML)
        self.mainArea.layout().addWidget(self.webview)

    def _create_layout(self):
        self._new_webview()
        box = gui.widgetBox(self.controlArea, 'Info')
        self.info = gui.label(box, self, 'Some info')

        box = gui.widgetBox(self.controlArea, 'Preferences')
    """
