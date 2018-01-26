# TODO: Documentation

import configparser
import os

class Config(object):
    
    def __init__(self, path):

        # The config file's path
        self.path = path
        
        # Create ConfigParser
        self.parser = configparser.SafeConfigParser()
        
        # Read the config file
        read = self.parser.read(path)
        
        # Check if reading worked
        if len(read)==0 or read[0]!=path:
            raise IOError("ERROR: Configuration file ({}) not found.".format(path))
        
    def get(self, key):
        if self.parser.has_option("all_settings", key):
            return os.path.expanduser(self.parser["all_settings"][key])
        else:
            raise KeyError("ERROR: Configuration file ({}) does not have the given key ({}).".format(self.path, key))
    
    def get_all(self, verbose=False):
        data = []
        for setting in self.parser["all_settings"]:
            data.append((setting, self.parser["all_settings"][setting]))
        if verbose:
            for d in data:
                print("Config '{}' has value '{}'".format(d[0], d[1]))
        return data
    
    def set(self, key, value):
        self.parser.set("all_settings", key, value)
        with open(self.path, "w") as f:
            # TODO: This whipes out all the comments!
            self.parser.write(f)
    
    def __str__(self):
        return "Config at '{}'".format(self.path)

# Debugging
if __name__ == "__main__":
    
    # File name of testing config file
    name = "unittest_config.ini"
    
    # Create a file with the correct format to be used
    f = open(name, "w")
    f.write("[all_settings]")
    f.close()
    
    # Config object
    print()
    print("Config() class unit test")
    print("========================")
    config = Config(name)
    print("config.get_all():")
    config.get_all(verbose=True)
    print("Set 'test':='value'")
    config.set("test", "value")
    print("config.get_all():")
    config.get_all(verbose=True)
    print("Set 'a':='1'")
    config.set("a", "1")
    print("Set 'b':='2'")
    config.set("b", "2")
    print("Set 'c':='3'")
    config.set("c", "3")
    print("Set 'd':='4'")
    config.set("d", "4")
    print("config.get_all():")
    config.get_all(verbose=True)
    print("Get 'd':", config.get("d"))
    print("Set 'c':='1337'")
    config.set("c", "1337")
    print("config.get_all():")
    config.get_all(verbose=True)
    print()
    
    # Delete the created file
    import os
    os.remove(name)
