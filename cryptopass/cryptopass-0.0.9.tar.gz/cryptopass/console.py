# -*- coding: utf-8 -*-

from . import user_managment as um
from . import encrypt
import pyperclip
import getpass as gp
from time import gmtime, strftime
import os


def input_data(cryptopass_user='skynet', exclude=[]):
    data = {#'cryptopass_user': '',
            'label': '',
            'user': '', 
            'password': '',
            'url': '',
            #'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            'hint': '',
            'notes': ''}
    
    for d in data:
        if not d in exclude: data[d] = input('{} = '.format(d))
    
    data.update({'cryptopass_user': cryptopass_user})
    data.update({'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime())})
    
    return data

def input_user(cryptopass_user, exclude=[]):
    print('\t if database left clear, it will be: {}\n'.format(um._PASS_DB_DEFAULT_))
    
    data = {#'cryptopass_user': '',
            'database': um._PASS_DB_DEFAULT_,
            #'salt': encrypt.get_random_salt(),
            #'born_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            #'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            #'counter': int(0),
            'notes': ''}
    
    for d in data:
        if not d in exclude: data[d] = input('{} = '.format(d))
    
    data.update({'cryptopass_user': cryptopass_user})
    if data['database'] == '': data.update({'database': um._PASS_DB_DEFAULT_})
    data.update({'salt': encrypt.get_random_salt()})
    data.update({'born_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime())})
    data.update({'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime())})
    data.update({'counter': int(0)})
    
    return data


def input_password(prompt='> password: '):
    password = gp.getpass(prompt=prompt)
    return password

#%% Cripto commands
def crypto_cmd_end(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t chau')    
    print('\n')

def crypto_cmd_h(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t crypto commands: \n')
    print('\t all: \tshow all valid entries for user/password.')
    print('\t All: \tshow all valid entries for user/password. (detailed)')
    print('\t all: \tshow all valid entries HINTS for user/password.')
    print('\t dbg: \texecute debug script (just for developing).')
    print('\t end: \texit cryptopass application.')
    print('\t h: \thelp please!')
    print('\t np: \tNew password entry.')
    print('\t p: \tGet a password for a given label.')
    print('\t p?: \tGet a password for a given label. Copied to clipboard only.')
    print('\t time: \tCalculate encryptio-decryption performance.')
    print('\t wd: \tPrint path of working directory.')
    
    print('\n')

def crypto_cmd_all(user,
                   user_database=um._USERS_DB_DEFAULT_, 
                   pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the followin password: \n')
    
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.get_valid_entries(cryptopass_password, salt, pass_database)
    if not found.empty: print(found[['label','password','date_time']])
    else: print('\t No entries found!')
    
    print('\n')

def crypto_cmd_All(user,
                   user_database=um._USERS_DB_DEFAULT_, 
                   pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the followin password: \n')
    
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.get_valid_entries(cryptopass_password, salt, pass_database)
    if not found.empty: print(found)
    else: print('\t No entries found!')
    
  
    print('\n')
    
def crypto_cmd_all_hints(user,
                         user_database=um._USERS_DB_DEFAULT_, 
                         pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the followin password: \n')
    
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.get_valid_entries(cryptopass_password, salt, pass_database)
    
    if not found.empty: print(found[['label','hint','date_time']])
    else: print('\t No entries found!')
    
    print('\n')
    
    
def crypto_cmd_dbg(user,
                   user_database=um._USERS_DB_DEFAULT_, 
                   pass_database=um._PASS_DB_DEFAULT_):
    # put here the script for debug

    return

def crypto_cmd_new_pass(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t New password entry: \n')
    new_data = input_data(user)
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    um.add_data_to_database_auto(new_data, 
                                 cryptopass_password, 
                                 user_database,
                                 pass_database)
    print('\t Successful!\n')
    
def crytpo_cmd_p(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t get the password for a label: \n')
    
    label = input('@{}> label: '.format(user))
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.decrypt_entry_with(cryptopass_password, 
                                  salt, 
                                  pass_database,
                                  'label',
                                  label)
    if not found.empty: 
        found_oldest = um.get_last_entry(found)
        print(found_oldest[['password','date_time']])
        
        found_password = found_oldest['password'][0]
        pyperclip.copy(found_password)
        print('\t password copied to clipboard!')
    else: print('\t No entries found!')
    
    print('\n')
    return

def crytpo_cmd_px(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t get the password for a label: \n')
    
    label = input('@{}> label: '.format(user))
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.decrypt_entry_with(cryptopass_password, 
                                  salt, 
                                  pass_database,
                                  'label',
                                  label)
    
    if not found.empty: 
        found_oldest = um.get_last_entry(found)
        print(found_oldest[['date_time']])
        found_password = found_oldest['password'][0]
        pyperclip.copy(found_password)
        print('\t password copied to clipboard!')
    else: print('\t No entries found!')
    
    print('\n')
    return


def crytpo_cmd_time(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    
    cryptopass_password = input_password('> password: ')
    test_str = input('> string for testing (press enter for default): ')
    if test_str == '': test_str = 'testing cryptopass'
    encrypt.get_password_performance_time(cryptopass_password)
    
    return

def crypto_cmd_wd(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t Working dir = {}'.format(os.getcwd()))
    return


def call_crytpo_cmd(user, 
                    cmd,
                    user_database=um._USERS_DB_DEFAULT_, 
                    pass_database=um._PASS_DB_DEFAULT_):
    
    crypto_cmd_dict = {'all': crypto_cmd_all,
                       'All': crypto_cmd_All,
                       'allh': crypto_cmd_all_hints,
                       'dbg': crypto_cmd_dbg,
                       'end': crypto_cmd_end,
                       'h': crypto_cmd_h,
                       'np': crypto_cmd_new_pass,
                       'p': crytpo_cmd_p,
                       'p?': crytpo_cmd_px,
                       'time': crytpo_cmd_time,
                       'wd': crypto_cmd_wd}
    
    if cmd in crypto_cmd_dict:
        crypto_cmd_dict[cmd](user, user_database, pass_database)
    else:
        print('Invalid command (press h for help):')
    return


def main():
    #%% Console starting message
    print('Cryptopass - version {}'.format(__import__('cryptopass').__version__))
    
    #%% init
    work_folder = um._WORK_FOLDER_
    user_db = um._USERS_DB_DEFAULT_
    pass_db = um._PASS_DB_DEFAULT_
    
    if not os.path.exists(work_folder):
        os.makedirs(work_folder)
        print('\t Work folder "{}" created.'.format(work_folder))
    
    user_db_ok = um.test_users_database(user_db)
    if user_db_ok:
        udb = um.load_users_database(user_db)
    else:
        print('\t User database error!')
    
    #%% Console   
    cryptopass_user = input('> cryptopass user: ')
    user_info, user_index = um.get_user_info(cryptopass_user, user_db)
       
        
    if not user_info.empty:
        loop = True
        
        # get the user database for passwords
        pass_db = user_info.iloc[0]['database']
        # test that database
        pass_db_ok = um.test_pass_database(user_db, pass_db)
        
        if pass_db_ok:
            pdb = um.load_passwords_database(pass_db) # not necessary by now
        else:
            print('\t Passwords database error!')
        
        while loop:
            crypto_cmd = input('> enter crypto command (press h for help): ')
            call_crytpo_cmd(cryptopass_user, crypto_cmd, user_db, pass_db)
            if crypto_cmd == 'end': break
        
        
    else:
        print('\t User "{}" has not been found!'.format(cryptopass_user))
        do_reg = input('\t Do you want create new user? [y/n]: ')
        if do_reg == 'y':
            print('\t Creating new user...')
            new_user = input_user(cryptopass_user)
            new_user, udb = um.add_new_user(new_user['cryptopass_user'],
                                            user_db,
                                            new_user['database'],
                                            new_user['notes'])
            ui, uidx = um.get_user_info(cryptopass_user, user_db)
            if not ui.empty: print('\t done!')
            else: print('\t error!')
        
    return


#%% Running console
#main()
    
if __name__ == "__main__":
    main()
