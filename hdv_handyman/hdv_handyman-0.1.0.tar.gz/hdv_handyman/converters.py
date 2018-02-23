from abc import ABCMeta, abstractmethod

class Converter():
    
    def __init__(self, input_name=None):
            
        self.input_name = input_name if input_name else 'Input'
    
    @abstractmethod
    def convert(self, input):
        pass

class SHA256(Converter):
    
    def convert(self, input):
        
        if not input:
            raise AttributeError('{input} cannot be empty'.format(input=self.input_name))
        
        import hashlib
        m = hashlib.sha256()
        m.update(input.encode('utf-8'))
        return m.hexdigest()