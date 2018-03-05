"""
file_actions
"""
import pathlib
import os
import shutil


class FileActions:
    """
    FileActions

    Wrapper for filesystem related actions within dfgen
    """
    def __init__(self, path='output'):
        """
        :param path: path where output should be written to, relative to cwd
        """
        self.path = os.getcwd() + '/' + path
        self._create_dir()

    def _create_dir(self):
        """
        :return:
        """
        pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_current_location():
        """
        :return: the current location of this script
        """
        return os.path.dirname(os.path.realpath(__file__))

    def write_file(self, filename, content):
        """
        :param filename: name of the output file
        :param content: contents of the file
        :return: full path to generated file
        """
        full_path = str(self.path) + '/' + filename
        new_file = open(full_path, 'w')
        new_file.write(content)
        new_file.close()
        return full_path

    def copy_to_path(self, source, destination_dir, destination_filename):
        """
        :param source: source file or directory
        :param destination_dir: destination directory
        :param destination_filename: destination file
        :return:
        """
        pathlib.Path(self.path + '/' + destination_dir).mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, self.path + '/' + destination_dir + '/' + destination_filename)
