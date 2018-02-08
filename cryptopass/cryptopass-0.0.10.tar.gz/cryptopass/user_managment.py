#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 14:20:04 2018

@author: f2a
"""
import pandas as pd
from time import gmtime, strftime
from cryptopass import encrypt

_SEP_ = ';'
_WORK_FOLDER_='./database/'
_USERS_DB_DEFAULT_NAME_ = 'default.udb'
_PASS_DB_DEFAULT_NAME_ = 'default.pdb'
_USERS_DB_DEFAULT_ = _WORK_FOLDER_ + _USERS_DB_DEFAULT_NAME_
_PASS_DB_DEFAULT_ = _WORK_FOLDER_ + _PASS_DB_DEFAULT_NAME_




def init_users_database(database=_USERS_DB_DEFAULT_):
    data = {'cryptopass_user': 'skynet',
            'database': _PASS_DB_DEFAULT_,
            'salt': encrypt.get_random_salt(),
            'born_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'counter': int(0),
            'notes': 'database has born!'}
    
    dataframe = pd.DataFrame(data, index=['cryptopass_check'])
     
    dataframe.to_csv(database, sep=_SEP_)
    
    return dataframe


def load_users_database(database=_USERS_DB_DEFAULT_):
    try:
        udb = pd.read_csv(database, sep=_SEP_, index_col=[0])
    except:
        udb = pd.Dataframe()
    return udb
 
    
def test_users_database(database=_USERS_DB_DEFAULT_):
    try:
        f = open(database,'r')
        f.close()
                
    except:
        # f = open(database,'w')
        # f.close()
        init_users_database(database)
        print('database does not exist! New database created: {}\n'.format(database))
    
    udb = load_users_database(database)
    
    # checking
    cryptopass_user = udb.at[('cryptopass_check','cryptopass_user')]
    check_database = udb.at[('cryptopass_check','database')]
    
    if cryptopass_user == 'skynet' and check_database == _PASS_DB_DEFAULT_:
        print('OK database file: {}\n'.format(database))
    else:
        print('Failed checking on database file: {}\n'.format(database))
        return False
    
    return True


def add_new_user(cryptopass_user, 
                 user_database=_USERS_DB_DEFAULT_,
                 pass_database=_PASS_DB_DEFAULT_,
                 notes=' '):
    data = {'cryptopass_user': cryptopass_user,
            'database': pass_database,
            'salt': encrypt.get_random_salt(),
            'born_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'counter': int(0),
            'notes': notes}
    dataframe = pd.DataFrame(data, index=['cpu_'+cryptopass_user])
    
    # try open the database
    try:
        udb = pd.read_csv(user_database, sep=_SEP_, index_col=[0])
    except:
        print('database reading error!')
        udb = pd.DataFrame()
        return
    
    ui, uidx = get_user_info(cryptopass_user, user_database)
    if ui.empty:
        # insert new user
        udb = udb.append(dataframe)
        udb.to_csv(user_database, sep=_SEP_)
    else: print('Cryptopass user "{}" already exists!'.format(cryptopass_user))
    
    return data, udb

def update_user(cryptopass_user, database=_USERS_DB_DEFAULT_, changes={}):
    # try open the database
    try:
        udb = pd.read_csv(database, sep=_SEP_, index_col=[0])
    except:
        print('database reading error!')
        return
    
    ui, user_index = get_user_info(cryptopass_user, database)
    if not ui.empty:
        for c in changes:
            try:
                if c in ['cryptopass_user',
                         'database',
                         'salt',
                         'born_time',
                         'last_change']:
                    print('database field "{}" is protected!'.format(c))
                else: ui[c] = changes[c]
            except:
                print('database field "{}" does not exist!'.format(c))
         
        dataframe = pd.DataFrame(ui, index=[user_index])
        udb.update(dataframe)
        udb.to_csv(database, sep=_SEP_)
            
    else: print('Cryptopass user "{}" does not exist!'.format(cryptopass_user))
        
    return ui

def delete_user(cryptopass_user, database=_USERS_DB_DEFAULT_, confirm=False):
    # try open the database
    try:
        udb = pd.read_csv(database, sep=_SEP_, index_col=[0])
    except:
        print('database reading error!')
        udb = pd.DataFrame()
        return
    
    ui, uidx = get_user_info(cryptopass_user, database)
    if not ui.empty:
        if confirm:
            if input('are you sure to delete "{}"? (y/n)'.format(cryptopass_user)) == 'y':
                # delet user
                udb = udb.drop(['cpu_'+ui['cryptopass_user'][0]])
                udb.to_csv(database, sep=_SEP_)
        else:        
            # delet user
            udb = udb.drop(['cpu_'+ui['cryptopass_user'][0]])
            udb.to_csv(database, sep=_SEP_)
    else: print('Cryptopass user "{}" does not exist!'.format(cryptopass_user))
    
    return udb
        

def get_user_info(cryptopass_user, database=_USERS_DB_DEFAULT_):
    udb = load_users_database(database)
    
    try:
        user_column_find = udb.loc[udb['cryptopass_user'] == cryptopass_user]
        user_index = udb[udb['cryptopass_user'] == cryptopass_user].index.values[0]
    except:
        user_column_find = pd.DataFrame()
        user_index = 'NaN'
    
    return user_column_find, user_index


def get_user_salt(cryptopass_user, database=_USERS_DB_DEFAULT_):
    ui, uidx = get_user_info(cryptopass_user, database)
    salt = ui.iloc[0]['salt']
    return salt

def get_new_user_index(cryptopass_user, database=_USERS_DB_DEFAULT_):
    
    
    ui, uidx = get_user_info(cryptopass_user, database)
    counter = int(ui.iloc[0]['counter'])
    
    update_user(cryptopass_user,
                database,
                changes={'counter': counter+1})
    
    new_index = cryptopass_user+'#'+str(counter)
    return new_index


def init_passwords_database(user_database=_USERS_DB_DEFAULT_, 
                            pass_database=_PASS_DB_DEFAULT_):
    data = {'cryptopass_user': 'skynet',
            'label': 'cryptopass',
            'user': 'guest',
            'email': ' ',
            'password': 'qwerty',
            'url': ' ',
            'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'hint': 'no chances!',
            'notes': 'database has born!'}
    
    ui, uidx = get_user_info(data['cryptopass_user'], database=user_database)
    salt = ui.iloc[0]['salt']
    
    key = encrypt.get_key('bazinga', salt)
    crypto_data = encrypt.encrypt_data(data, key)
    
    dataframe = pd.DataFrame(crypto_data, index=[encrypt.encrypt_str(key,'cryptopass_check')])
     
    dataframe.to_csv(pass_database, sep=_SEP_)
    
    return dataframe


def test_pass_database(user_database=_USERS_DB_DEFAULT_, 
                       pass_database=_PASS_DB_DEFAULT_):
    try:
        f = open(pass_database,'r')
        f.close()
        
    except:
        # f = open(database,'w')
        # f.close()
        init_passwords_database(user_database, pass_database)
        print('database does not exist! New database created: {}\n'.format(pass_database))
    
    udb = load_users_database(user_database)
    cryptopass_salt = udb.at[('cryptopass_check','salt')]
    
    # checking
    finding = decrypt_entry_with('bazinga',
                                 cryptopass_salt,
                                 pass_database,
                                 'label',
                                 'cryptopass')
    
    cryptopass_user = finding.iloc[0]['cryptopass_user']
    password = finding.iloc[0]['password']
    
    if cryptopass_user == 'skynet' and password == 'qwerty':
        print('OK database file: {}\n'.format(pass_database))
    else:
        print('Failed checking on database file: {}\n'.format(pass_database))
        return False
    
    return True


def load_passwords_database(pass_database=_PASS_DB_DEFAULT_):
    try:
        pdb = pd.read_csv(pass_database, sep=_SEP_, index_col=[0])
    except:
        pdb = pd.DataFrame()
    return pdb


def add_data_to_database(data, password, salt, index='None', pass_database=_PASS_DB_DEFAULT_):
    key = encrypt.get_key(password, salt)
    crypto_data = encrypt.encrypt_data(data, key)
    
    dataframe = pd.DataFrame(crypto_data, index=[encrypt.encrypt_str(key,index)])
    
    pdb = load_passwords_database(pass_database)
    pdb = pdb.append(dataframe)
    pdb.to_csv(pass_database, sep=_SEP_)
    
    return pdb

def add_data_to_database_auto(data, 
                              password, 
                              user_database=_USERS_DB_DEFAULT_, 
                              pass_database=_PASS_DB_DEFAULT_):
    cryptopass_user = data['cryptopass_user']
    user_salt = get_user_salt(cryptopass_user, user_database)
    new_index = get_new_user_index(cryptopass_user, user_database)
    
    pdb = add_data_to_database(data, password, user_salt, new_index, pass_database)

    return pdb 

def get_valid_entries(password, salt, database):
    pdb = pd.read_csv(database, sep=_SEP_, index_col=[0])
    findings = pd.DataFrame()
    
    for index, row in pdb.iterrows():
        row = row.to_frame()
        row = row.transpose()
        
        decrypt_row = decrypt_dataframe(row, password, salt)
        decrypt_index = decrypt_row.index.values[0]
        
        if decrypt_index != 'cp_pass_error':
            findings = findings.append(decrypt_row)
    
    return findings


def get_entry_with(database, field, dataval):
    db = pd.read_csv(database, sep=_SEP_, index_col=[0])
    findings = pd.DataFrame()
    
    for d in dataval:
        try:
            column_find = db.loc[db[field] == d]
            findings = findings.append(column_find)
        except:
            column_find = False
    
    return findings

    
def decrypt_dataframe(dataframe, password, salt):
    key = encrypt.get_key(password, salt)
    
    crypto_data = dataframe.to_dict('records')
    
    data = encrypt.decrypt_data(crypto_data[0], key)
    data_index=encrypt.decrypt_str(key, dataframe.index.values[0])
    if data_index == '': data_index = 'cp_pass_error'
    
    decrypt_dataframe = pd.DataFrame(data, index=[data_index])
         
    return decrypt_dataframe
    

def decrypt_entry_with(password, salt, database, field, dataval):
    pdb = pd.read_csv(database, sep=_SEP_, index_col=[0])
    findings = pd.DataFrame()

    for index, row in pdb.iterrows():
        row = row.to_frame()
        row = row.transpose()
        
        decrypt_row = decrypt_dataframe(row, password, salt)
        
        try:
            if decrypt_row.iloc[0][field] == dataval:
                findings = findings.append(decrypt_row)
        except:
            None
    
    return findings


def get_last_entry(entries):
    find = entries.loc[entries['date_time'] == max(entries['date_time'])]
    
    return find