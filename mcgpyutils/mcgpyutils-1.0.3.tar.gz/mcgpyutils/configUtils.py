import json

from .fileSystemUtils import FileSystemUtils

class ConfigUtils:
    def __init__(self):
        self.json_config = None
        self.fsu = FileSystemUtils()
        self.config_location = None


    '''
    Reads and saves a JSON config file.

    @param path: the path to the JSON config file
    @raise FileNotFoundError: the specified config file was not found
    '''
    def parse_json_config(self, path):
        try:
            self.fsu.file_exists(path)

            with open(path) as config:
                self.json_config = json.load(config)
                self.config_location = path
        except FileNotFoundError as e:
            raise e


    '''
    Returns a field from a JSON config file.

    @return: the value of the specified config field, None is the field does not
             exist
    '''
    def get_json_config_field(self, field):
        if field in self.json_config:
            return self.json_config[field]
        else:
            return None


    '''
    Returns the entire parsed JSON config file as a dict.

    @return: a dict representing the parsed JSON config file.
    '''
    def get_json_config(self):
        return self.json_config


    '''
    Returns the location of the config file that was loaded.

    @return: the path to the config file that was loaded
    '''
    def get_config_location(self):
        return self.config_location
