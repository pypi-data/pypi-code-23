from . import lowlevel as c

print(dir(c))
Image = c.Image



'''
print(dir(c))
class Image(c.Image_baseclass):
    pass

class Image(c.wrapped_pointer):
    def __del__(self):
        c.Image_delete(self.p)
        
'''

    
        
        