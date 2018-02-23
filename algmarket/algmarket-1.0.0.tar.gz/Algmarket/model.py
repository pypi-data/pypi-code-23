from enum import Enum

ModelObjectType = Enum('ModelObjectType','file directory')

class ModelObject(object):
    def __init__(self, model_object_type):
        self.model_object_type = model_object_type

    def is_file(self):
        '''Returns whether object is a file'''
        return self.model_object_type is ModelObjectType.file

    def is_dir(self):
        '''Returns whether object is a directory'''
        return self.model_object_type is ModelObjectType.directory

    def get_type(self):
        '''Returns type of this ModelObject'''
        return self.model_object_type

    def set_attributes(self):
        '''Sets attributes about the directory after querying the Model API'''
        raise NotImplementedError