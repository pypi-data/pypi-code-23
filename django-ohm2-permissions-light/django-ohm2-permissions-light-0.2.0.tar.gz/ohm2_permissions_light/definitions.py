from . import settings


class Base(Exception):
    
    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)

class ModelNotFound(Base):
    def __init__(self):
        super(ModelNotFound, self).__init__("Model not found")