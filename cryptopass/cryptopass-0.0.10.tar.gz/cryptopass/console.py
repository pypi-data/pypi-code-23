# -*- coding: utf-8 -*-

from cryptopass import user_managment as um
from cryptopass import encrypt
from cryptopass import config
import pyperclip
import getpass as gp
from time import gmtime, strftime
import os

session = {'username': '',
           'wd': '',
           'user_db': '',
           'pass_db': ''}

def input_data(cryptopass_user='skynet', exclude=[]):
    data = {#'cryptopass_user': '',
            'label': '',
            'user': '', 
            'email': '',
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
    print('\t if database left clear, it will be: <working dir>/{}\n'.format(
            um._PASS_DB_DEFAULT_NAME_))
    
    data = {#'cryptopass_user': '',
            'database': um._PASS_DB_DEFAULT_NAME_,
            #'salt': encrypt.get_random_salt(),
            #'born_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            #'date_time': strftime("%Y-%m-%d-%H:%M:%S", gmtime()),
            #'counter': int(0),
            'notes': ''}
    
    for d in data:
        if not d in exclude: data[d] = input('{} = '.format(d))
    
    data.update({'cryptopass_user': cryptopass_user})
    if data['database'] == '': data.update({'database': um._PASS_DB_DEFAULT_NAME_})
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
    #print('\t chau')    
    print('\n')

def crypto_cmd_h(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t crypto commands: \n')
    print('\t all: \t show all valid entries for user/password.')
    print('\t All: \t show all valid entries for user/password. (detailed)')
    print('\t all: \t show all valid entries HINTS for user/password.')
    print('\t dbg: \t execute debug script (just for developing).')
    print('\t end: \t exit of cryptopass.')
    print('\t h: \t help please!')
    print('\t logout: logout user session.')
    print('\t np: \t New password entry.')
    print('\t p: \t Get a password for a given label.')
    print('\t p?: \t Get a password for a given label. Copied to clipboard only.')
    print('\t time: \t Calculate encryptio-decryption performance.')
    print('\t wd: \t Print path of working directory.')
    
    print('\n')

def crypto_cmd_all(user,
                   user_database=um._USERS_DB_DEFAULT_, 
                   pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the following password: \n')
    
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.get_valid_entries(cryptopass_password, salt, pass_database)
    if not found.empty: print(found[['label','user','password','email','date_time']])
    else: print('\t No entries found!')
    
    print('\n')

def crypto_cmd_All(user,
                   user_database=um._USERS_DB_DEFAULT_, 
                   pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the following password: \n')
    
    cryptopass_password = input_password('@{}> password: '.format(user))
    
    salt = um.get_user_salt(user,user_database)
    found = um.get_valid_entries(cryptopass_password, salt, pass_database)
    if not found.empty: print(found)
    else: print('\t No entries found!')
    
  
    print('\n')
    
def crypto_cmd_all_hints(user,
                         user_database=um._USERS_DB_DEFAULT_, 
                         pass_database=um._PASS_DB_DEFAULT_):
    print('\t showing all entries with the following password: \n')
    
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

def crypto_cmd_logout(user,
                 user_database=um._USERS_DB_DEFAULT_, 
                 pass_database=um._PASS_DB_DEFAULT_):
    print('\t logging out... bye {}\n'.format(user))
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
        print(found_oldest[['user','password','date_time']])
        
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
        print(found_oldest[['user','date_time']])
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
                       'logout': crypto_cmd_logout,
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

#%% Console commands
def call_console_cmd(session, cmd='h', params=[]):
    console_cmd_dict={'udb': console_cmd_udb,
                      'end': console_cmd_end,
                      'h': console_cmd_help,
                      'login': console_cmd_login,
                      'wd': console_cmd_wd}
    if cmd in console_cmd_dict:
        session = console_cmd_dict[cmd](session, params)
    else:
        print('Invalid command (press h for help):')
    return session

def console_cmd_help(session, params=[]):
    print('\t console commands: \n')
    print('\t end: \texit of cryptopass.')
    print('\t h: \thelp please!')
    print('\t login:\tcryptopass user login.')
    print('\t udb: \tChange users database.')
    print('\t wd: \tChange working directory.')
    
    print('\n')
    return session

def console_cmd_udb(session, params=[]):
    user_db = input('\t Define user database (left empty for default): ')
    if user_db == '': user_db = um._USERS_DB_DEFAULT_NAME_
        
    if config.set_active_user_database(user_db):
        session['user_db'] = session['wd'] + user_db
        user_db_ok = um.test_users_database(session['user_db'])
        if user_db_ok:
            um.load_users_database(session['user_db'])
        else:
            print('\t User database error!')
    else:
        print('\t User database error!')
    return session

def console_cmd_end(session, params=[]):
    print('\t chau')    
    print('\n')
    return session

def console_cmd_login(session, params=[]):
    cryptopass_user = input('> cryptopass user: ')
    
    user_info, user_index = um.get_user_info(cryptopass_user, session['user_db'])
               
    if not user_info.empty:
        # get the user database for passwords
        pass_db = user_info.iloc[0]['database']
        # test that database
        pass_db_ok = um.test_pass_database(session['user_db'], pass_db)
        
        if pass_db_ok:
            um.load_passwords_database(pass_db) # not necessary by now
            session['pass_db'] = pass_db
        else:
            print('\t Passwords database error!')
        
        session['username'] = cryptopass_user
        
    else:
        print('\t User "{}" has not been found!'.format(cryptopass_user))
        do_reg = input('\t Do you want create new user? [y/n]: ')
        if do_reg == 'y':
            print('\t Creating new user...')
            new_user = input_user(cryptopass_user)
            
            pass_db = session['wd']+new_user['database']
            
            new_user, udb = um.add_new_user(new_user['cryptopass_user'],
                                            session['user_db'],
                                            pass_db,
                                            new_user['notes'])
            ui, uidx = um.get_user_info(cryptopass_user, session['user_db'])
            if not ui.empty:
                session['username'] = cryptopass_user
                print('\t done!')
            else: print('\t error!')
            
            # test that database
            pass_db_ok = um.test_pass_database(session['user_db'], pass_db)
            
            if pass_db_ok:
                um.load_passwords_database(pass_db) # not necessary by now
                session['pass_db'] = pass_db
            else:
                print('\t Passwords database error!')
            
    return session

def console_cmd_wd(session, params=[]):
    wd = input('\t Define working directory (left empty for default): ')
    if wd == '': wd = um._WORK_FOLDER_
        
    if config.set_working_dir(wd):
        if not os.path.exists(wd):
            os.makedirs(wd)
            print('\t Working folder "{}" created.'.format(wd))
        
        session['wd'] = wd
        # load the user database in taht directory
        session = console_cmd_udb(session)
    else:
        print('\t Operation error!')
    return session

#%% 
def init():
    wd = um._WORK_FOLDER_
    user_db = um._USERS_DB_DEFAULT_NAME_
    #pass_db = um._PASS_DB_DEFAULT_NAME_
    
    if not config.check_init():
        wd = input('\t Define working directory (left empty for default): ')
        if wd == '': wd = um._WORK_FOLDER_
        user_db = input('\t Define user database (left empty for default): ')
        if user_db == '': user_db = um._USERS_DB_DEFAULT_NAME_
        
        config.make_init_file(wd, user_db)
    else:
        wd = config.get_working_dir()
        user_db = config.get_active_user_database()
    
    if not os.path.exists(wd):
        os.makedirs(wd)
        print('\t Working folder "{}" created.'.format(wd))
    
    user_db_ok = um.test_users_database(wd+user_db)
    if user_db_ok:
        um.load_users_database(wd+user_db)
    else:
        print('\t User database error!')
    
    session = {'username': '',
               'wd': wd,
               'user_db': wd+user_db,
               'pass_db': ''}
    return session

def main():
    #%% Console starting message
    print('Cryptopass - version {}'.format(__import__('cryptopass').__version__))
    
    #%% init
    session = init()
    print('\t Working directory: {}'.format(session['wd']))
    
    #%% Console  
    console_on = True
    console_cmd = ''
    crypto_cmd = ''
    
    while console_on:
        if session['username'] == '':
            # user not logged in
            console_cmd = input('> enter console command (press h for help): ')
            session = call_console_cmd(session,console_cmd)
            if console_cmd == 'end': break
        ##
        else:
            loop = True
            while loop:
                crypto_cmd = input('@{}> enter crypto command (press h for help): ' \
                                   .format(session['username']))
                call_crytpo_cmd(session['username'], 
                                crypto_cmd, 
                                session['user_db'], 
                                session['pass_db'])
                if crypto_cmd == 'logout' or crypto_cmd == 'end': 
                    session['username'] = ''
                    break
        
        if crypto_cmd == 'end': 
            session = call_console_cmd(session,'end')
            break
        
    return


#%% Running console
#main()
    
if __name__ == "__main__":
    main()
