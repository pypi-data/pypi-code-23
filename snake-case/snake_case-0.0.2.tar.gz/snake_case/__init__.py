# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 18:37:53 2018
update pkd: start powershell as admin and then pip install . --upgrade

After that update on pypi
#$ pip install twine
#$ python setup.py sdist bdist_wheel
#$ twine register dist/project_name-x.y.z.tar.gz
#$ twine register dist/mypkg-0.1-py2.py3-none-any.whl

$ twine upload dist/*

@author: MGO
"""

def to_any_case(string):
    string = string.lower()
    return string
