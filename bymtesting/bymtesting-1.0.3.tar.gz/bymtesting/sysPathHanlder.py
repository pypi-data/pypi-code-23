import sys
import os


class sysPathHandler:

    def __init__(self):
        self.currfolder = os.getcwd()
        self.parentFolder = os.path.abspath("..")

    def exists(self, path):
        path = os.path.join(path)
        arr = sys.path
        if path in arr:
            print("Sys.path contains: {}".format(path))
            return True
        return False

    def addToSysPath(self, path):
        if self.exists(path) == False:
            sys.path.append(path)
            output = "\nAdded {} to system path ...\n".format(path)
            print(output)

    def removeFromSysPath(self, path):
        if self.exists(path):
            sys.path.remove(path)
            output = "\nRemoved {} from system path ...\n".format(path)
            print(output)

    def AddCurrentTestingToSysPath(self):
        self.addToSysPath(self.parentFolder)
        self.addToSysPath(self.currfolder)

    def RemoveCurrentTestingFromSysPath(self):
        self.removeFromSysPath(self.parentFolder)
        self.removeFromSysPath(self.currfolder)
