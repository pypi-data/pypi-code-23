#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 10:16:09 2018

@author: f2a
"""

from cryptopass import user_managment as um
import json

_INIT_FILE_ = './cryptopass.json'

def check_init(EnPrint=False):
    try:
        f = open(_INIT_FILE_,'r')
        f.close()
        if EnPrint: print('\t init file is rigth!')
    except:
        if EnPrint: print('\t error checking init file!')
        return False
    
    return True


def make_init_file(working_dir=um._WORK_FOLDER_, 
                   user_database=um._USERS_DB_DEFAULT_NAME_):
    f = open(_INIT_FILE_,'w')
    
    init_str = {'working_dir': working_dir,
                'user_db': user_database}
    
    init_json = json.dumps(init_str)
    f.write(init_json)
    
    f.close()
    return

def get_working_dir():
    
    try:
        f = open(_INIT_FILE_,'r')
        init_json = json.load(f)
        wd = init_json['working_dir']
        f.close()

    except:
        print('\t error reading init file!')
        wd = ''
    
    return wd

def set_working_dir(wd):
    
    try:
        f = open(_INIT_FILE_,'r')
        init_json = json.load(f)
        f.close()
        
        init_json['working_dir'] = wd
        init_json = json.dumps(init_json)
        
        f = open(_INIT_FILE_,'w')
        f.write(init_json)
        f.close()

    except:
        print('\t error reading init file!')
        return False
    
    return True


def get_active_user_database():
    try:
        f = open(_INIT_FILE_,'r')
        init_json = json.load(f)
        udb = init_json['user_db']
        f.close()

    except:
        print('\t error reading init file!')
        udb = ''
    
    return udb

def set_active_user_database(user_database):
    try:
        f = open(_INIT_FILE_,'r')
        init_json = json.load(f)
        f.close()
        
        init_json['user_db'] = user_database
        init_json = json.dumps(init_json)
        
        f = open(_INIT_FILE_,'w')
        f.write(init_json)
        f.close()

    except:
        print('\t error reading init file!')
        return False
    
    return True
    