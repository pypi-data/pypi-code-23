from comtypes import client
import os


EXPORT_FORMATS = ['png', 'gif', 'jpg', 'tif']


class File:
    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError
        self.filename = filename
        self.app = client.CreateObject('Powerpoint.Application')
        self.presentation = self.app.Presentations.Open(
            os.path.abspath(self.filename),
            ReadOnly=True,
            WithWindow=False)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f'<PowerPoint file "{self.filename}">'

    def close(self):
        self.presentation.Close()
        self.app.Quit()

    def export(self, export_format, path=None):
        if export_format not in EXPORT_FORMATS:
            raise ValueError(f'"{export_format}" not supported as export '
                             f'format, use one of these: '
                             f'{", ".join(EXPORT_FORMATS)}')
        if path is None:
            path = os.path.splitext(os.path.abspath(self.filename))[0]
        else:
            path = os.path.splitext(os.path.abspath(path))[0]
        self.presentation.Export(path, export_format)
