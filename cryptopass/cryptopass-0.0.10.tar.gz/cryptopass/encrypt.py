#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 15:43:04 2018

@author: f2a
"""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import time
from time import gmtime, strftime


def get_random_salt():
    return base64.b64encode(os.urandom(32)).decode('utf-8')

def get_key(password, salt):
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key

def get_token(key):
    return Fernet(key)

def encrypt_str(key, str_in):
    token = get_token(key)
    
    return token.encrypt(str_in.encode()).decode()
    
def decrypt_str(key, str_in, print_messages=False):
    token = get_token(key)
    
    try:
        str_out = token.decrypt(str_in.encode()).decode()
        return str_out
    except:
        if print_messages: print('wrong password!')
        return ''
    
def encrypt_data(data, key):
    crypto_data = {'cryptopass_user': encrypt_str(key,data['cryptopass_user']),
                   'label': encrypt_str(key,data['label']),
                   'user': encrypt_str(key,data['user']),
                   'email': encrypt_str(key,data['email']), 
                   'password': encrypt_str(key,data['password']),
                   'url': encrypt_str(key,data['url']),
                   'date_time': encrypt_str(key,strftime("%Y-%m-%d-%H:%M:%S", gmtime())),
                   'hint': encrypt_str(key,data['hint']),
                   'notes': encrypt_str(key,data['notes'])}
    
    return crypto_data

def decrypt_data(crypto_data, key):
    data = {'cryptopass_user': decrypt_str(key,crypto_data['cryptopass_user']),
            'label': decrypt_str(key,crypto_data['label']),
            'user': decrypt_str(key,crypto_data['user']),
            'email': decrypt_str(key,crypto_data['email']), 
            'password': decrypt_str(key,crypto_data['password']),
            'url': decrypt_str(key,crypto_data['url']),
            'date_time': decrypt_str(key,crypto_data['date_time']),
            'hint': decrypt_str(key,crypto_data['hint']),
            'notes': decrypt_str(key,crypto_data['notes'])}
    
    return data

def get_password_performance_time(password, test_str='testing cryptopass'):
    print("\t Next values are computed with this computer's performace: ")
    
    time_ini = time.time()
    x = 2+2
    time_end = time.time()
    sum_time = time_end-time_ini
    print('\t sum of 2+2={} needs = {}[us]'.format(x,sum_time*pow(10,6)))
    
    
    time_ini = time.time()
    salt = get_random_salt()
    time_end = time.time()
    salt_time = time_end-time_ini
    print('\t SALT generation time = {}[s]'.format(salt_time))
    
    time_ini = time.time()
    key = get_key(password, salt)
    time_end = time.time()
    key_time = time_end-time_ini
    print('\t KEY generation time = {}[s]'.format(key_time))
    
    time_ini = time.time()
    token = get_token(key)
    time_end = time.time()
    token_time = time_end-time_ini
    print('\t TOKEN generation time = {}[s]'.format(token_time))
    
    str_in = test_str.encode()
    print('\t String to be encrypted: {}'.format(str_in))
    
    time_ini = time.time()
    str_encrypted = token.encrypt(str_in)
    time_end = time.time()
    encryption_time = time_end-time_ini
    print('\t ENCRYPTION time = {}[s]'.format(encryption_time))
    
    time_ini = time.time()
    str_decrypted = token.decrypt(str_encrypted)
    time_end = time.time()
    decryption_time = time_end-time_ini
    print('\t DECRYPTION time = {}[s]'.format(decryption_time))
    
    if str_in == str_decrypted:
        print('\t encription-decription chain OK!')
    else:
        print('\t encription-decription chain FAIL!')
    
    pass_length = len(password)
    all_pass_time = pow((26+26+10),pass_length)*(key_time+decryption_time)
    print('\t Time to probe all password with {} characters (A..Z,a..z,0..9) = ' \
          .format(pass_length))
    print('\t\t {}[seconds]'.format(all_pass_time))
    print('\t\t {}[hours]'.format(all_pass_time/(60*60)))
    print('\t\t {}[days]'.format(all_pass_time/(60*60*24)))
    print('\t\t {}[years]'.format(all_pass_time/(60*60*24*365)))
    
    return
    
    
    
    
    
    
    