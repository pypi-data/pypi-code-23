"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import logger
import json
import yaml


class File(object):
    """ 
    Implement a text file methods
    e.g.: read, write, etc...
    
    Args:
        file_path: full path to file 
    """
    
    
    #==================================================================
    def __init__(self, file_path):
        """ Constructor """
        self.file = file_path
        
    #==================================================================
    def read(self):
        """ Open the file and return its content """
        try:
            with open(self.file, 'r') as f:
                try: 
                    return f.read()
                except Exception as e:
                    logger.out.exception("Exception while trying to read: '{}', {}"\
                                     .format(self.file, e))
        except Exception as e:
            logger.out.exception("Exception while trying to open: '{}', {}"\
                             .format(self.file, e))            
        return None
    
    

#==================================================================
#==================================================================
#==================================================================
class Json(File):
    '''
    Implement any Json method
    '''
    
    #==================================================================
    def loads(self):
        self.load()
        
        
    #==================================================================
    def load(self):
        """
        Return a dictionary representing the Json file content
        """
        return json.loads(self.read())
    
    
    #==================================================================
    def dump(self, json_dictionary):
        """
        Dump the given json_dictionary to self.file
        """
        with open(self.file, 'w') as f:
            json.dump(json_dictionary, f, indent=4)
            
            
            
#==================================================================
#==================================================================
#==================================================================
class Yaml(File):
    """ Implement YAML file format """

    #==================================================================
    def load(self):
        """
        Return a dictionary representing the Yaml file content
        """
        return yaml.load(self.read())
 
 
    #==================================================================
    def dump(self, dictionary):
        """
        Dump the given dictionary to self.file
        """
        with open(self.file, 'w') as f:
            yaml.dump(dictionary, f, indent=4)
        
        