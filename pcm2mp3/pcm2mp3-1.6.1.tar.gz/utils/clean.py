'''
Created on 2 Dec 2017

@author: julianporter
'''
from setuptools import Command
import shutil
import os

class Cleaner(Command) :
    """setuptools rigorous clean"""
    
    description="removes build and dist files for a truly clean build"
    user_options=[]
    
    def __init__(self,dist,**kwargs):
        super(Cleaner,self).__init__(dist,**kwargs)
        
    def initialize_options(self):
        self.directories=[]
        self.files=[]
    
    def finalize_options(self):
        self.directories=['build','dist','pcm2mp3.egg-info']
        self.files=[]
    
    def run(self):
        self.run_command('clean')
        print("Deep cleaning")
        
        for directory in self.directories:
            try:
                shutil.rmtree(directory)
                print("{} deleted".format(directory))
            except FileNotFoundError:
                print("{} does not exist, so not deleted...".format(directory))
            except Exception as e:
                print("{} : {}".format(e.__class__.__name__,e))
        for file in self.files:
            try:
                os.remove(file)
                print("{} deleted".format(directory))
            except FileNotFoundError:
                print("{} does not exist, so not deleted...".format(directory))
            except Exception as e:
                print("{} : {}".format(e.__class__.__name__,e))
            
        
        