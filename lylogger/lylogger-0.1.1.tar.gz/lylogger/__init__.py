import logging
from logging.handlers import RotatingFileHandler

class Lylogger:
    def __init__(self,file_path=None,silent=False,mode='w',
                 setlevel='debug',formatter=None,rotate=False,maxsize=50,maxcount=10):
        if formatter ==None:
            formatter = logging.Formatter('[Time:%(asctime)s][File:%(filename)s][Function: %(funcName)s][Line:%(lineno)d][%(levelname)s]::%(message)s')
        self.pprint = logging.getLogger('')
        __level =  {'debug':logging.DEBUG,'info':logging.INFO,'warning':logging.WARNING,'critical':logging.CRITICAL}
        self.pprint.setLevel(__level[setlevel])
        if silent == False:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            self.pprint.addHandler(console)

        if file_path != None and rotate is False:
            file = logging.FileHandler(file_path, mode=mode, encoding='utf8')
            file.setFormatter(formatter)
            self.pprint.addHandler(file)
        elif file_path != None and rotate is True:
            Rthandler = RotatingFileHandler('myapp.log', maxBytes=maxsize * 1024 * 1024, backupCount=maxcount)
            Rthandler.setFormatter(formatter)
            self.pprint.addHandler(Rthandler)


