import os


def appDir():
    full_path = os.path.realpath(__file__)

    return os.path.dirname(full_path)+"/../"

def init(app):
    global mainApp
    mainApp= app



def getMainApp():
    return mainApp