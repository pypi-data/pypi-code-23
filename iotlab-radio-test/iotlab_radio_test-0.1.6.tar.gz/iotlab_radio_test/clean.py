import os

import shutil


class CleanLog(object):
    """ Clean merge and avg log files
    """
    def __init__(self, parsed_dir, image_dir):
        self.parsed_dir = parsed_dir
        self.image_dir = image_dir

    def clean_dir(self):
        if os.path.exists(self.parsed_dir):
            shutil.rmtree(self.parsed_dir)
        if os.path.exists(self.image_dir):
            shutil.rmtree(self.image_dir)
