# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 18:37:53 2018
update pkd: start powershell as admin and then pip install . --upgrade

After that update on pypi
pip install twine
python setup.py sdist bdist_wheel
twine register dist/snake_case-0.0.2.tar.gz
twine upload dist/snake_case-0.0.2.tar.gz

$ twine upload dist/*

@author: MGO
"""

from .text import to_any_case
