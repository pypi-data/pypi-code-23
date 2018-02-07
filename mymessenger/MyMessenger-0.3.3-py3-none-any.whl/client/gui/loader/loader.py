import shutil
import os

from ..repo.models import session
from ..repo.repo import Repo


class Loader:
    """Loader for avatars."""

    def __init__(self, folder_name='files'):
        self.folder_name = folder_name
        self.repo = Repo(session)
        self.check_folder()

    def check_folder(self):
        """Create folder for files if not exists"""
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)

    def load(self, file_path):
        """Load avatar and save path to repo."""
        path = os.path.join(self.folder_name, file_path)
        shutil.copy(file_path, path)
        self.repo.add('avatar', path)
