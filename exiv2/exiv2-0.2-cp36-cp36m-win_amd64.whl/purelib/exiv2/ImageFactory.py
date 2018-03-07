from . import lowlevel as c

class ImageFactory:
    @staticmethod
    def open(path_or_buffer):
        return c.ImageFactory_open(path_or_buffer)
        
        