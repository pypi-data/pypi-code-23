# -----------------------------------------------------------------
# zeus: log.py
#
# Define zeus logging tools
#
# Copyright (C) 2016, Christophe Fauchard
# -----------------------------------------------------------------

"""
Submodule: log.file

Log an trace

Copyright (C) 2016-2017, Christophe Fauchard
"""

import os
import logging
import logging.handlers
import zeus


class Log():

    """
    Log Class with switch and display level capabilities
    """
    def __init__(self,
                 file_name=None,
                 number=7,
                 size=1048576,
                 frequence=None,
                 stdout='Yes',
                 level=logging.INFO
                 ):
        self.file_name = file_name
        if file_name is not None:
            self.dirname = zeus.file.Path(os.path.dirname(file_name))
        self.frequence = frequence
        self.number = number
        self.size = size
        self.stdout = stdout
        self.level = level

        #
        # create the logger
        #
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        #
        # create formatter log
        #
        self.formatter = logging.Formatter(
            '%(asctime)s :: %(module)s :: %(levelname)s :: %(message)s')

        if self.file_name is not None:
            if frequence is None:

                #
                # create size based rotation log
                #
                self.file_handler = logging.handlers.RotatingFileHandler(
                    self.file_name,
                    'a',
                    self.size,
                    self.number)
                self.file_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.file_handler)
                self.file_handler.setLevel(self.level)

            else:

                #
                # create date based rotation log
                #
                self.file_handler = logging.handlers.TimedRotatingFileHandler(
                    self.file_name,
                    when=self.frequence,
                    interval=1,
                    backupCount=self.number)
                self.file_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.file_handler)
                self.file_handler.setLevel(self.level)

        #
        # create stdout handler
        #
        self.stream_handler = logging.StreamHandler()
        self.logger.addHandler(self.stream_handler)
        self.stream_handler.setLevel(self.level)

    def set_level(self, level):
        self.level = level
        if self.file_name is not None:
            self.file_handler.setLevel(self.level)
        self.stream_handler.setLevel(self.level)
