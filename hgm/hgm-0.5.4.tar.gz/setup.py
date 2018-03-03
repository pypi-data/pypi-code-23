#!/usr/bin/python
# _*_ encoding: UTF-8 _*_

from distutils.core import setup        

setup(  name = 'hgm',
        version = '0.5.4',
        packages=['hgm'], 
        py_modules = ['kdfe','preproc','ggmf','computetensor'],
        description = 'Hyper-graph matching API', 
        author = 'Bing SHI',            
        author_email = 'bing.shi@aliyun.com',
        url = 'https://github.com/bing-shi/HGM',
)
  
