# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 00:22:23 2018

@author: MGO
"""

from re import sub

def to_any_case(string):

    # sep_in
    string = sub(r' ', '_', string)

    # parsing_option 1
    string = sub(r'([A-Z][a-z]+)', '_\\1_' , string)
    string = sub(r'([A-Z]{2, })', '_\\1_' , string)
    string = sub(r'([A-Z][A-Z]{1}[[A-Z][a-z]]*)', '_\\1_', string)
    string = sub(r'([A-Z][a-z]\d]*)', '_\\1_', string)
    
    string = sub(r'_+', '_', string)
    string = sub(r'^_|_$', '', string)

    # case
    string = string.lower()

    # return
    return string

