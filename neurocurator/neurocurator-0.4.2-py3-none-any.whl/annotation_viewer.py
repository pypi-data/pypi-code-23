#!/usr/bin/env python3.4

from PySide.QtCore import QUrl

__author__ = "Pierre-Alexandre Fonta"
__maintainer__ = "Pierre-Alexandre Fonta"

import sys

from PySide.QtGui import QApplication, QMainWindow
from PySide.QtWebKit import QWebView, QWebSettings

PDFJS = "file:///Users/fonta/Downloads/pdfjs-1.9.426-dist/web/viewer.html"
PDF = "file:///Users/fonta/test.pdf"

# class PDFViewer(QWebView):
#     pdf_viewer_page = "/Users/fonta/Downloads/pdfjs-1.9.426-dist/web/viewer.html"
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.settings = QWebSettings.globalSettings()
#         self.settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True )
#         self.settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True )
#         self.settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True )
#         nam = QNetworkAccessManager()
#         page = QWebPage(self)
#         page.setNetworkAccessManager(nam)
#         self.setPage(page)
#         self.loadFinished.connect(self.onLoadFinish)
#         self.setUrl(QUrl(self.pdf_viewer_page))
#
#     def onLoadFinish(self, success):
#         if success:
#             self.page().mainFrame().evaluateJavaScript("init();")


if __name__ == "__main__":
    sys.argv.append("--disable-web-security")
    app = QApplication(sys.argv)

    win = QMainWindow()
    web_view = QWebView()
    web_view.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
    web_view.settings().setAttribute(QWebSettings.AcceleratedCompositingEnabled, True)
    web_view.settings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
    web_view.settings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
    web_view.settings().setAttribute(QWebSettings.LocalStorageEnabled, True)
    web_view.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
    web_view.settings().setAttribute(QWebSettings.PluginsEnabled, True)
    url = QUrl("{}?file={}#disableWorker=true".format(PDFJS, PDF))
    web_view.load(url)
    win.setCentralWidget(web_view)
    win.show()
    sys.exit(app.exec_())
