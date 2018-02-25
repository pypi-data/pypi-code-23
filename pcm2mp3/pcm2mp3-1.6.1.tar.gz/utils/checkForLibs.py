'''
Created on 4 Dec 2017

@author: julianporter
'''

from tempfile import mkdtemp
import os
import shutil
from distutils import ccompiler, sysconfig, errors 
from sys import argv

HelloWorld='''
#include<iostream>
int main(int argc, char* argv[])
{
    std::cout << "hello world" << std::endl;
    return 0;
}
'''

class LibraryError(Exception):
    
    def __init__(self,message,inner=None):
        super(LibraryError,self).__init__()
        self.message=message
        self.inner=inner
        
    def __str__(self):
        if not self.inner:
            st="Library exception: {}"
            args=[self.message]
        else:
            st="Library exception: {}  Inner {} : {}"
            args=[self.message,type(self.inner).__name__,str(self.inner)]
        return st.format(*args)


class CheckLibrary(object):
    
    def __init__(self,*libs):
        self.libraries=libs
        self.tmp=mkdtemp(prefix='_libsearch')
        self.src=os.path.join(self.tmp,'hello.cpp')
        self.exe=os.path.join(self.tmp,'hello')
        self.results=dict()

    def _makeSource(self):
        with open(self.src,'w') as file:
            file.write(HelloWorld)
    
    def _cleanup(self):
        try:
            shutil.rmtree(self.tmp)
        except:
            pass
        
    def test(self):
        try:
            self._makeSource()
        except Exception as e:
            raise LibraryError('Cannot create source file',inner=e)    
        
        try:
            compiler = ccompiler.new_compiler()
            if not isinstance(compiler, ccompiler.CCompiler):
                raise errors.CompileError("Compiler is not valid!")
            sysconfig.customize_compiler(compiler)
            o=compiler.compile([self.src])
            
            for lib in self.libraries:
                try:
                    exe=self.exe+"_"+lib
                    compiler.link_executable(o,exe,libraries=[lib,'stdc++'])
                    self.results[lib]=True
                except Exception as e:
                    self.results[lib]=False
                  
        except errors.CompileError as e:
            raise LibraryError('Compilation problems',inner=e)
        except Exception as e:
            raise LibraryError('General error',inner=e)
        finally:
            self._cleanup()
            
    def __getitem__(self,key):
        return self.results[key]
    
    def __iter__(self):
        return iter(self.results)
    
    
            
    
if __name__=='__main__':
    c=CheckLibrary(*argv[1:])
    c.test()
    for lib in c:
        print("{} : {}".format(lib,c[lib]))

    
    
    
            
        

