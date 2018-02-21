"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import logging
import sys
import os


#======================================================================
#   CLASS: TextLogger
#======================================================================
class TextLogger(logging.Logger):
    """
    Print logs to text file.
    
    Args:
        name (str):        logger name
        level (logging):   logging.DEBUG, etc... refer to logging docs
        filename (str):    report file name
        mode (str):        refer to logging docs
        
    """ 
    
    def __init__(self, name     = "text_logger", 
                       level    = logging.DEBUG,
                       rootdir  = None,
                       filename = "testlog.txt", 
                       mode     = 'w'):
        
        super(TextLogger, self).__init__(name=name, level=level)
        
        self.rootdir = rootdir
        report_dir = self.get_report_dir()
        if report_dir:
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            """ write to file """
            formater = TextFormater()
            file_handler  = TextFileHandler(report_dir+"/"+filename, mode)
            file_handler.setFormatter(formater)
            self.addHandler(file_handler)
            
            """ write to console """
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formater)
            self.addHandler(stream_handler)


    def get_current_dir(self):
        """ Return current execution directory """
        return os.path.dirname(os.path.abspath(sys.argv[0]))
         
    
    def get_report_dir(self):
        """ Return a directory path, where reports should be saved 
        
        Returns:
            if self.rootdir is initialize then return directory  
            otherwise return None  
        """
        
        base_dir = "reports"
        if self.rootdir:
            return '{}/{}'.format(self.rootdir, base_dir)
        return None 


#======================================================================
#   CLASS: TextFormater
#======================================================================
class TextFormater(logging.Formatter):
    """ Sets a global line format for each print. """
    def __init__(self):
        FORMAT = '%(asctime)s - %(module)s:%(funcName)s():%(lineno)d - %(levelname)s - %(message)s'
        super(TextFormater, self).__init__(FORMAT)


#======================================================================
#   CLASS: TextFileHandler
#======================================================================
class TextFileHandler(logging.FileHandler):
    """ Main handler required to """
    def __init__(self, *args):
        super(TextFileHandler, self).__init__(*args)


#======================================================================
#   CLASS: Links
#======================================================================
class Links():
    """
    Hold list of links and their names. 
    
    Test developer can add link to any network/Internet location during test.
    The added links will be displayed by the Ochrus Server at its HTML report.   
    """
    def __init__(self):
        self._links = []
        
    def append(self, link, name=None):
        if name is None:
            name = link
        self._links.append({"name":"{}".format(name),
                             "link":"{}".format(link)})
    def get_links(self):
        return self._links
    
    def del_links(self):
        self._links = []
        
out = TextLogger()
links = Links()

