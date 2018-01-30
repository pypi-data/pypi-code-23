import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QLabel,
    QAction, QFileDialog, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon
from client import User
from handlers import GuiReciever
from ui_forms.new_chat import *

class