# -*- coding: utf-8 -*-
# __author__ = 'elkan1788@gmail.com'

from ppytools.cfgreader import ConfReader

import logging

logging.basicConfig(level=logging.INFO,
                    encoding='UTF-8', format='%(asctime)s [%(levelname)s] {%(name)-10s} - %(message)s')


class ProjectConfig(object):
    """ProjectConfig
    """
    def __init__(self, *conf_paths):
        self.cr = ConfReader(*conf_paths)

    def getHiveConf(self):
        return self.cr.getValues('HiveServer')

    def getEmailServer(self):
        return self.cr.getValues('EmailServer')

    def getJobInfo(self):
        return self.cr.getValues('JobInfo')

    def getCSVFolder(self):
        return self.cr.getValues('CSVFolder')['folder']

    def getCSVFile(self):
        return self.cr.getValues('CSVFile')

    def getCSVHead(self):
        return self.cr.getValues('CSVHead')

    def getHQLScript(self):
        return self.cr.getValues('HQLScript')

    def getEmailInfo(self):
        return self.cr.getValues('EmailInfo')

