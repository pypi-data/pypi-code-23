import sys
import getpass
import requests
import json
import os
import zipfile

from settings import ACCEPTED_DBS, ACCEPTED_LANGS, BASE_URL, CRED_PATH, OPT_PATH

if '--local' in sys.argv:
    BASE_URL = 'http://localhost:8000'

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def extract_options():
    f = open(OPT_PATH, 'r')
    data = f.readline()
    if data:
        data = json.loads(data[:-1])
    else:
        data = {}
    options = f.readline()
    if options:
        options = json.loads(options)
    else:
        options = {}
    return data, options

def login():
    data = {}
    sys.stdout.write('Please input your email: ')
    data['email'] = input()
    data['password'] = getpass.getpass(prompt='Please input your password: ')
    data['password1'] = data['password']
    data['password2'] = data['password']
    return requests.post(BASE_URL + '/api/auth/login/', data=data)

def signup():
    data = {}
    sys.stdout.write('Please input your email: ')
    data['email'] = input()
    sys.stdout.write('Please input your first name: ')
    data['first_name'] = input()
    sys.stdout.write('Please input your last name: ')
    data['last_name'] = input()
    data['password'] = getpass.getpass(prompt='Please input your password: ')
    data['password1'] = data['password']
    data['password2'] = data['password']
    return requests.post(BASE_URL + '/api/auth/register/', data=data)

def register():
    sys.stdout.write('Do you have a HelloDeploy account y/n: ')
    resp = input()
    if resp == 'y':
        resp = login()
    elif resp == 'n':
        resp = signup()
    else:
        print('Sorry, invalid input')
        return register()
    key = json.loads(resp.content)['key']
    f = open(CRED_PATH, 'w')
    f.write(key)
    return key


def upload(token, data, options):
    if 'zip_option' not in options:
        sys.stdout.write('Do you want to zip current contents(z) of dir or upload your own zip file(u): ')
        options['zip_option'] = input()
    if options['zip_option'] == 'z':
        zipf = zipfile.ZipFile('.Archive.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir('.', zipf)
        zipf.close()
        files = {'files': open('.Archive.zip', 'rb')}
    elif options['zip_option'] == 'u':
        sys.stdout.write('Please input the path of the project zip file: ')
        options['zip_file'] = input()
        if not os.path.isfile(options['zip_file']):
            print('Sorry that file does not exist')
            return upload(token, data, options)
        files = {'files': open(options['zip_file'], 'rb')}
    else:
        print('Sorry, did not understand the input')
        options.pop('zip_option')
        return upload(token, data, options)
    if 'name' not in data:
        sys.stdout.write('Please input your project name: ')
        data['name'] = input()
    if 'lang' not in data:
        sys.stdout.write('Please input the language your app uses p2=python2, p3=python3, n=node, r=ruby, h=html: ')
        data['lang'] = input()
        data['lang'] = ACCEPTED_LANGS[data['lang']]
    if data['lang'] == 'HTML':
        do_stuff = 5
    elif data['lang'] in ACCEPTED_LANGS.values():
        if 'cmd' not in data:
            sys.stdout.write('Please input the command to run the app: ')
            data['cmd'] = input()
        if 'port' not in data:
            sys.stdout.write('Please input the port your app runs on: ')
            data['port'] = input()
        if 'db' not in data:
            sys.stdout.write('Please input the Database your app uses z=none, n=node, p=postgres, s=sql3lite, m=mysql: ')
            data['db'] = input()
            data['db'] = ACCEPTED_DBS[data['db']]
        if db == 'none':
            do_stuff = 5
        elif data['db'] in ACCEPTED_DBS.values():
            if 'db_port' not in data:
                sys.stdout.write('Please input the port your Database uses: ')
                data['db_port'] = input()
            if 'db_name' not in data:
                sys.stdout.write('Please input the name of your Database: ')
                data['db_name'] = input()
            if 'db_username' not in data:
                sys.stdout.write('Please input the Database username: ')
                data['db_username'] = input()
            if 'db_password' not in data:
                sys.stdout.write('Please input the Database password: ')
                data['db_password'] = input()
            if 'db_env' not in data:
                sys.stdout.write('Please input the environment Variable for Database Host: ')
                data['db_env'] = input()
    headers = {'Authorization': 'Token ' + token}
    r = requests.post(BASE_URL + '/api/upload/', data=data, headers=headers, files=files)
    os.remove('.Archive.zip')
    f = open('.options', 'w')
    f.write(json.dumps(data) + '\n')
    f.write(json.dumps(options))
    f.close()
    print(r)
    print(r.content)
