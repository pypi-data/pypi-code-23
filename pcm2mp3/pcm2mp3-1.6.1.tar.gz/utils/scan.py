'''
Created on 10 Feb 2018

@author: julianporter
'''




import re

import os

if 'scandir' in dir(os):
    scandir = os.scandir
else:
    from os.path import join, isdir
    class FileInfo(object):
        def __init__(self,d,name):
            self.name=name
            self.path=join(d,name)
            
        def is_dir(self):
            return isdir(self.path)
     
    class ScanList(object):
        
        def __init__(self,ls):
            self.ls=ls
            
        def __iter__(self):
            return iter(self.ls)
        
        def close(self):
            pass       
    
    def scandir(folder):
        names=os.listdir(folder)
        return ScanList([FileInfo(folder,name) for name in names])
        




class Scanner(object):
    
    def __init__(self,root='.',matcher="[a-zA-Z0-9]+\.cpp"):
        self.root=root
        self.matcher=re.compile(matcher)
        self.files=[]
        
    def _scan(self,folder):
        out=scandir(folder)
        for entry in out:
            if entry.is_dir():
                #print('Starting recursive scan of {}'.format(entry.path))
                self._scan(entry.path)
                
            else:
                #print("Checking {} - {}".format(entry.name,self.matcher.match(entry.name)))
                if self.matcher.match(entry.name):
                    self.files.append(entry.path)
        out.close()
        
    def __call__(self):
        self._scan(self.root)
        return self.files
        