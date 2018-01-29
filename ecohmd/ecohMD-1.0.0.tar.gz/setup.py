#!/usr/bin/env python3

from distutils.core import setup

setup(
    name         =    'ecohMD',
    version      =    '1.0.0',
    py_modules   =    ['ecohMD', 'readItems', 'judge', 'parse'],
    data_files   =    ['codeJS.css', 'codeStyle.css', 'quoteStyle.css', 'prism.css', 'prism.js'],
    author       =    'Ecohnoch',
    author_email =    '542305306@qq.com',
    #url          =     'https://upload.pypi.org/legacy/',
    description  =    'markdown to html'
)