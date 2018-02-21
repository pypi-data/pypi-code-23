"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import os
import sys
from txtfile import Yaml
CLASS_KEY="class"

class Setup(object):
    """ 
    Create class according to configuration file.

    Setups uses to generate Python classes from a text configuration file.

    Notes:
        A Setup file is written in YAML format.
        Its content include a dictionary as followed:
        - each key at the dictionary is the object instance name.
        - the key value is also a dictionary that include:
          the 'class' key and the constructor fields.  
          e.g.:  
              server1:
                  {'class': 'my_package.my_sub_module.MyObject1'
                   'field1': 'value1'
                   'field2': 'value2'
                  }
              server2:
                  {'class': 'my_package.my_sub_module.MyObject2'
                   'field1': 'value1'
                  }
        The 'class' key must include full Python class path (see example above)
        and must be sit at the PATHONPATH                        

    Args:
        class_dirs (list): optional, list of directories to add to PAYTHONPATH 

    Returns:
        The new created classes will be available as a new member of
        current Setup class.
        Their name will be the key name as define at the given 'params' dict

    """
    
    #=========================================================================
    def __init__(self, class_dirs=None):
        self.class_dirs = class_dirs
       
    #=========================================================================
    def load(self, setup_name, dir_list=None):
        """ 
        Load the setup config file.
        
        Once loading a setup file, all its defining classes are available
        as Setup members, e.g.: for the above dictionary example 
        import setup
        env = setup.Setup.load("setup.yml")
        env.server1.ip
        env.server2.ip
        
        Args:
            setup_name (str): configuration file name without the .yaml extension
                              and without the path to file 
            dir_list (list):  Optional default=None: 
                              list of directories where the setup file can be found.
                              this directory should be initialized by pytest-ochrus
                              plug-in.
        
        """
        global setup_dirs
        setup_file = "{}.yaml".format(setup_name)
        dirc = self._find_setup_dir(setup_file, dir_list)
        setup_file_path = "{}/{}".format(dirc, setup_file)
        
        if dirc is None:
            print "Exiting... can't find '{}' at: '{}'".format(setup_file, setup_dirs)
            sys.exit(1)
            
        #with open("{}/{}".format(dir, setup_file)) as f:
        #    setup_dict = yaml.load(f)
        setup_dict = Yaml(setup_file_path).load()
        self._create_classes(setup_dict)


    #=========================================================================
    def _find_setup_dir(self, setup_file, dir_list=None):
        global setup_dirs
        if dir_list is None:
            dir_list = setup_dirs
        
        for _dir in dir_list:
            if os.path.exists("{}/{}".format(_dir, setup_file)):
                return _dir
        return None  

 
    #=========================================================================
    def _create_classes(self, setup_dict):
        """
        Create the classes and add them as self members
        """
        for key in setup_dict.keys():
            if type(setup_dict[key]) is dict:
                if self._get_class_name(**setup_dict[key]) is not None:
                    exec("self.{}=self._create_class(**{})".format(key, setup_dict[key]))   
                else:
                    exec("self.{}=self._create_var(**{})".format(key, setup_dict[key]))
            else:
                exec("self.{}=self._create_var(*{})".format(key, setup_dict[key]))


    #=========================================================================
    def _create_var(self, *args, **kwargs):
        if args is not None:
            newvar = eval("{}".format(args))   #create tuple
        else: 
            newvar = eval("{"+"{}".format(kwargs)+"}") #create dict
        
        return newvar


    #=========================================================================
    def _get_class_name(self, **kwargs):        
        try:
            cls = kwargs.pop(CLASS_KEY)
            return cls
        except:
            return None         

        
    #=========================================================================    
    def _create_class(self, **kwargs):
        """ 
        Create class and return a reference to the new created class.
        
        Args:
            **kwargs (dictionary) e.g.: {"class": "my_module.MyClass"
                                         "field1": "value1"}
            
        Returns:
            reference to the new created class
            None: when fails
        """      
        try:
            cls = kwargs.pop(CLASS_KEY)
        except:
            print("Setups() can't find "+CLASS_KEY+" key! at: '{}'".format(kwargs))
            return None
                 
        module_name, class_name = self._split_classname(cls)
        
        """ add objects directories to PYTHONPATH """
        self._path_append()
        
        try:
            if module_name!=None:
                exec("import {}".format(module_name))
        except Exception as e:
            print("Can't import '{}', got exception: '{}'".format(module_name, e))
        
        if module_name!=None:
            class_def = module_name+"."+class_name + "(**{})".format(kwargs)
        else:
            class_def = class_name + "(**{})".format(kwargs)
            
        try:    
            newclass = eval(class_def)
            return newclass
        except Exception as e:
            print("Setups: Got exception: '{}', while creating class: '{}'".format(e, class_def))
            return None
    
    
    #=========================================================================
    def _split_classname(self, class_full_path):
        """
        Split full Python path for two:
        1. the class path 
        2. the class name 
        
        Args:
            class_full_path - e.g.: my_package.my_module.MyClass
        
        Returns:
            Tuple: (my_package.my_module, MyClass)
        """
        try:
            last_dot_index = class_full_path.rindex(".")
            module_name = class_full_path[:last_dot_index]
            class_name  = class_full_path[last_dot_index+1:]
        except: #if only class was given 
            module_name = None
            class_name  = class_full_path 
        return (module_name, class_name)

 
    #=========================================================================
    def _path_append(self):
        """
        Add class directories to Python path 
        (ignore if already exists)
        """
        if self.class_dirs:
            class_dirs = self.class_dirs.split(':')
            for class_dir in class_dirs:
                if(not self._in_list(class_dir, sys.path)):
                    sys.path.append(class_dir)
                      
    
    #=========================================================================
    def _in_list(self, find_me, lst):
        """
        Return True: if 'find_me' exist at the 'lst'
        Return False: if not exists
        """
        for item in lst:
            if item.strip() == find_me.strip():
                return True
        return False

    
""" should be initialized by config.OchrusConfig """
setup_dirs = []    
    
    
        
        
        
        
   