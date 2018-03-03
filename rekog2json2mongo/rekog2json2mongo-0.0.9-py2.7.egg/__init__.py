from .base import face2folder2mango
from .compare import face2compare

def main():
    flag = raw_input('Facial detect API (F) or Compare faces API (C), F/C ?')
    
    if flag.lower()=='f':
        
        print 'starting Facial detect API'
        path=raw_input('path of folder that contains pictures: ')
        face2folder2mango(path)
        
    elif flag.lower()=='c':  
        
        print 'starting Compare faces API'
        print 'prepare a folder of images 
        path=raw_input('path of folder that contains pictures (name.jpg, name_cpr.jpg collections) to compare: ')
        face2compare(path)        
        
    else:
        print 'invalid input'
        pass