from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PIL import Image
from PIL.ImageQt import ImageQt

from .utils import center
from .ui.ConnectDialog import Ui_ConnectDialog
from .ui.AboutDialog import Ui_AboutDialog
from .ui.ProfileDialog import Ui_ProfileDialog
from .repo.models import session
from .repo.repo import Repo
from ...utils import get_square_image


class ConnectUI(QtWidgets.QDialog):
    """Start window to set connection params."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent().is_started = False
        self.ui = Ui_ConnectDialog()
        self.ui.setupUi(self)
        self.ui.pushButtonConnect.clicked.connect(self.connect)
        center(self)

    def connect(self):
        """Get params and transfer to parent"""
        ip, port = self.ui.lineEditIP.text().split(':')
        port = int(port)
        login = self.ui.lineEditLogin.text()
        password = self.ui.lineEditPassword.text()
        self.parent().ip = ip
        self.parent().port = port
        self.parent().login = login
        self.parent().password = password
        self.parent().is_started = True
        self.accept()


class AboutUI(QtWidgets.QDialog):
    """Window to show about info."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        center(self)


class ProfileUI(QtWidgets.QDialog):
    """Window to change profile."""
    def __init__(self, parent=None):
        super().__init__(parent)
        center(self)
        self.repo = Repo(session)
        self.new_avatar = None
        self.initUI()
        self.getAvatar()

    def initUI(self):
        self.ui = Ui_ProfileDialog()
        self.ui.setupUi(self)
        self.ui.pushButtonBrowse.clicked.connect(self.loadAvatar)
        self.ui.pushButtonSave.clicked.connect(self.save)
        # Disable not ready features
        self.ui.lineEditLogin.setDisabled(True)
        self.ui.lineEditPassword.setDisabled(True)

    def save(self):
        self.saveAvatar()
        self.close()

    def getAvatar(self):
        image_bytes = self.repo.get_image()
        if image_bytes:
            width = self.ui.labelAvatarImage.width()
            size = width, width
            image = Image.frombytes('RGBA', size, image_bytes)
            self.updateAvatar(image)

    def saveAvatar(self):
        if self.new_avatar:
            self.repo.add_image(self.new_avatar.tobytes())

    def updateAvatar(self, image):
        img_tmp = ImageQt(image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        self.ui.labelAvatarImage.setPixmap(pixmap)

    def loadAvatar(self):
        """Get avatar from disk."""
        fname = QFileDialog.getOpenFileName(self, 'Выберите аватар', '/home')[0]
        if not fname:
            return 0
        image = Image.open(fname)
        image = get_square_image(image)
        width = self.ui.labelAvatarImage.width()
        image = image.resize((width, width), Image.ANTIALIAS)
        self.new_avatar = image.convert('RGBA')
        self.updateAvatar(image)
