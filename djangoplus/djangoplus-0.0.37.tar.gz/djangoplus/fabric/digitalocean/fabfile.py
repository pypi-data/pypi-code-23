# -*- coding: utf-8 -*-
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import exists, append, contains
from os import path
import sys
import os
import json
import datetime
import time
import StringIO

username = 'root'
project_dir = os.getcwd()
project_name = project_dir.split('/')[-1]
remote_project_dir = '/var/opt/%s' % project_name

if 'deploy' in sys.argv or 'undeploy' in sys.argv or 'update' in sys.argv or 'push' in sys.argv or 'backupdb' in sys.argv:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%s.settings' % project_name)
    from django.conf import settings

env.user = username
env.connection_attempts = 10

GIT_INGORE_FILE_CONTENT = '''*.pyc
.svn
.DS_Store
.DS_Store?
._*
.idea/*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
.project
.pydevproject
.settings/*
sqlite.db
media/*
mail/*
fabfile.pyc
'''
NGINEX_FILE_CONTENT = '''server {
    client_max_body_size 100M;
    listen %(port)s;
    server_name %(server_name)s;
    access_log /var/opt/%(project_name)s/logs/nginx_access.log;
    error_log /var/opt/%(project_name)s/logs/nginx_error.log;
    location /static {
        alias /var/opt/%(project_name)s/static;
    }
    location /media {
        alias /var/opt/%(project_name)s/media;
    }
    location / {
        proxy_pass_header Server;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_set_header X-Real_IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        proxy_pass http://localhost:%(local_port)s/;
    }
}
'''
SUPERVISOR_FILE_CONTENT = '''[program:%(project_name)s]
directory = /var/opt/%(project_name)s
user = www-data
command = /var/opt/%(project_name)s/gunicorn_start.sh
stdout_logfile = /var/opt/%(project_name)s/logs/supervisor_out.log
stderr_logfile = /var/opt/%(project_name)s/logs/supervisor_err.log
'''
GUNICORN_FILE_CONTENT = '''#!/bin/bash
set -e
source /var/opt/.virtualenvs/%(project_name)s/bin/activate
mkdir -p /var/opt/%(project_name)s/logs
cd /var/opt/%(project_name)s
exec gunicorn %(project_name)s.wsgi:application -w 1 -b 127.0.0.1:%(port)s --timeout=600 --user=www-data --group=www-data --log-level=_debug --log-file=/var/opt/%(project_name)s/logs/gunicorn.log 2>>/var/opt/%(project_name)s/logs/gunicorn.log
'''
LIMITS_FILE_CONTENT = '''
*               soft     nofile           65536
*               hard     nofile           65536
root            soft     nofile           65536
root            hard     nofile           65536
'''
BASHRC_FILE_CONTENT = '''
export WORKON_HOME=/var/opt/.virtualenvs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
'''


def _debug(s):
    print '[%s] %s\n' % (datetime.datetime.now(), s)


def _available_port():
    nginex_dir = '/etc/nginx/sites-enabled'
    port = 8000
    with cd(nginex_dir):
        files = run('ls').split()
        files.remove('default')
        if project_name in files:
            files = [project_name]
        if files:
            command = "grep  localhost %s | grep -o '[0-9]*'" % ' '.join(files)
            ports = run(command).split()
            ports.sort()
            port = ports[-1]
            if project_name not in files:
                port = int(port) + 1
    _debug('Returning port %s!' % port)
    return int(port)


def _check_local_keys():
    local_home_dir = local('echo $HOME', capture=True)
    local_ssh_dir = path.join(local_home_dir, '.ssh')
    local_public_key_path = path.join(local_ssh_dir, 'id_rsa.pub')
    if not os.path.exists(local_ssh_dir):
        _debug('Creating dir %s...' % local_ssh_dir)
        local('mkdir %s' % local_ssh_dir)
        if not path.exists(local_public_key_path):
            local("ssh-keygen -f %s/id_rsa -t rsa -N ''" % local_ssh_dir)

    key = open(local_public_key_path, 'r').read().strip()
    _debug('Checking if private key was uploaded to digital ocean...')
    url = 'https://api.digitalocean.com/v2/account/keys'
    params = (settings.DIGITAL_OCEAN_TOKEN, url)
    command = '''curl -X GET -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s"''' % params
    response = local(command, capture=True)
    # print response
    if key not in response:
        _debug('Uploading private key to digital ocean...')
        params = (settings.DIGITAL_OCEAN_TOKEN, 'Default', key, url)
        command = '''curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' -d '{"name":"%s","public_key":"%s"}' "%s"''' % params
        response = local(command, capture=True)
        # print response


def _check_remote_keys():
    local_home_dir = local('echo $HOME', capture=True)
    local_ssh_dir = path.join(local_home_dir, '.ssh')
    local_public_key_path = path.join(local_ssh_dir, 'id_rsa.pub')
    local_private_key_path = path.join(local_ssh_dir, 'id_rsa')

    remote_home_dir = run('echo $HOME')
    remote_ssh_dir = path.join(remote_home_dir, '.ssh')
    remote_public_key_path = path.join(remote_ssh_dir, 'id_rsa.pub')
    remote_private_key_path = path.join(remote_ssh_dir, 'id_rsa')
    remote_private_known_hosts_path = path.join(remote_ssh_dir, 'known_hosts')
    if not exists(remote_ssh_dir):
        _debug('Creading remote dir %s...' % remote_ssh_dir)
        run('mkdir -p %s' % remote_ssh_dir)
        _debug('Creating empty file %s...' % remote_private_known_hosts_path)
        run('touch %s' % remote_private_known_hosts_path)

    with cd(remote_ssh_dir):
        public_key = open(local_public_key_path, 'r').read()
        private_key = open(local_private_key_path, 'r').read()
        _debug('Checking if public key is in file %s...' % remote_public_key_path)
        if not contains(remote_public_key_path, public_key):
            _debug('Appending public key in file %s...' % remote_public_key_path)
            append(remote_public_key_path, public_key)
        _debug('Checking if private key is in file %s...' % remote_private_key_path)
        if not contains(remote_private_key_path, private_key):
            _debug('Appending private key in file %s...' % remote_private_key_path)
            append(remote_private_key_path, private_key)
        run('chmod 644 %s' % remote_public_key_path)
        run('chmod 600 %s' % remote_private_key_path)
        _debug('Checking if %s is in file %s...' % (env.hosts[0], remote_private_known_hosts_path))
        if not contains(remote_private_known_hosts_path, env.hosts[0]):
            _debug('Appending %s in file %s...' % (env.hosts[0], remote_private_known_hosts_path))
            run('ssh-keyscan %s >> %s' % (env.hosts[0], remote_private_known_hosts_path))


def _check_repository():
    with cd('/home'):
        git_dir = '/home/git'
        if not exists(git_dir):
            run('adduser --disabled-password --gecos "" git')
            run('mkdir /home/git/.ssh && chmod 700 /home/git/.ssh')
            run('touch /home/git/.ssh/authorized_keys && chmod 600 /home/git/.ssh/authorized_keys')
            run('cat /root/.ssh/authorized_keys >> /home/git/.ssh/authorized_keys')
            run('chown -R git.git /home/git/.ssh/')
        project_git_dir = '/home/git/%s.git' % project_name
        if not exists(project_git_dir):
            run('mkdir %s' % project_git_dir)
            run('cd %s && git init --bare' % project_git_dir)
            run('chown -R git.git %s' % project_git_dir)
    return 'git@%s:%s.git' % (env.hosts[0], project_name)


def _setup_local_repository():
    _debug('Checking if local project is a git project...')
    if not path.exists(path.join(project_dir, '.git')):
        with cd(project_dir):
            _debug('Making local project a git project...')
            repository_url = _check_repository()
            local('git init')
            local('git remote add origin "%s"' % repository_url)
            local('echo "..." > README.md')
            local('echo "%s" > .gitignore' % GIT_INGORE_FILE_CONTENT)


def _setup_remote_repository():
    _debug('Checking if the project was cloned in remote server...')
    if not exists(remote_project_dir):
        with cd('/var/opt'):
            _debug('Cloning project in remote server...')
            repository_url = _check_repository()
            run('git clone %s %s' % (repository_url, project_name))
            run('chown -R www-data.www-data %s' % project_name)
    _debug('Updating project in remote server...')
    with cd(remote_project_dir):
        run('git pull origin master')


def _push_local_changes():
    _debug('Checking if project has local changes...')
    now = datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")
    with cd(project_dir):
        if 'nothing to commit' not in local('git status', capture=True):
            _debug('Comminting local changes...')
            files = []
            for file_name in local('ls', capture=True).split():
                if file_name not in GIT_INGORE_FILE_CONTENT or file_name == 'fabfile.py':
                    files.append(file_name)
            files.append('.gitignore')
            for pattern in NGINEX_FILE_CONTENT.split():
                if pattern in files:
                    files.remove(pattern)
            local('git add %s' % ' '.join(files))
            local("git commit -m '%s'" % now)
        _debug('Uploading local changes...')
        local('git push origin master')


def _setup_remote_env():
    _debug('Checking if the virtualenv dir was created in remote server...')
    virtual_env_dir = '/var/opt/.virtualenvs'
    if not exists(virtual_env_dir):
        _debug('Creating dir %s' % virtual_env_dir)
        run('mkdir -p %s' % virtual_env_dir)
    project_env_dir = path.join(virtual_env_dir, project_name)
    _debug('Checking if virtualenv for the project was created...')
    if not exists(project_env_dir):
        with shell_env(WORKON_HOME=virtual_env_dir):
            _debug('Creating virtual env %s' % project_name)
            run('source /usr/local/bin/virtualenvwrapper.sh && mkvirtualenv %s' % project_name)


def _setup_remote_project():
    with cd(remote_project_dir):
        _debug('Checking project requirements..')
        if exists('requirements.txt'):
            virtual_env_dir = '/var/opt/.virtualenvs'
            with shell_env(WORKON_HOME=virtual_env_dir):
                _debug('Installing/Updating project requirements...')
                run(
                    'source /usr/local/bin/virtualenvwrapper.sh && workon %s && pip install -U -r requirements.txt' % project_name)
        _debug('Checking if necessary dirs (logs, media and static) were created...')
        run('mkdir -p logs')
        run('mkdir -p static')
        run('mkdir -p media')
        _debug('Granting access to www-data...')
        run('chown -R www-data.www-data .')


def _check_domain():
    if settings.DIGITAL_OCEAN_DOMAIN:

        url = 'https://api.digitalocean.com/v2/domains'
        params = (settings.DIGITAL_OCEAN_TOKEN, url, settings.DIGITAL_OCEAN_DOMAIN)
        command = '''curl -X GET -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s/%s"''' % params
        _debug('Checking if domain %s was created...' % settings.DIGITAL_OCEAN_DOMAIN)
        data = json.loads(local(command, capture=True))
        if data.get('id', None) == 'not_found':
            _debug('Creating domain %s...' % settings.DIGITAL_OCEAN_DOMAIN)
            ip_address = env.hosts[0]
            params = (settings.DIGITAL_OCEAN_TOKEN, settings.DIGITAL_OCEAN_DOMAIN, ip_address, url)
            command = '''curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' -d '{"name":"%s","ip_address":"%s"}' "%s"''' % params
            data = json.loads(local(command, capture=True))

        ip_address = None

        try:
            ip_address = local('host %s' % settings.DIGITAL_OCEAN_DOMAIN, capture=True).split(' ')[-1].strip()
        except Exception as e:
            print e

        if ip_address != env.hosts[0]:
            _debug('The domain is not activated yet. The ip %s is going to be used for the deploy.' % env.hosts[0])
            return None

    return settings.DIGITAL_OCEAN_DOMAIN


def _print_remote_url():
    file_path = '/etc/nginx/sites-enabled/%s' % project_name
    file_descriptor = StringIO.StringIO()
    get(file_path, file_descriptor)
    file_content = file_descriptor.getvalue()
    server_name = None
    port = None
    for line in file_content.split('\n'):
        if 'server_name ' in line:
            server_name = line.strip().split()[1].replace(';', '')
        elif 'listen ' in line:
            port = line.strip().split()[1].replace(';', '')
    url = 'http://%s' % server_name
    if int(port) != 80:
        url = '%s:%s' % (url, port)
    print(u'\n\n\nURL: %s\n\n' % url)


def _setup_nginx_file():
    file_path = '/etc/nginx/sites-enabled/%s' % project_name
    _debug('Checking nginx file %s...' % file_path)
    checked_domain = _check_domain()
    if exists(file_path):
        file_descriptor = StringIO.StringIO()
        get(file_path, file_descriptor)
        file_content = file_descriptor.getvalue()
        if checked_domain and checked_domain not in file_content:
            content = []
            for line in file_content.split('\n'):
                if 'server_name ' in line:
                    line = line.replace('server_name', 'server_name %s' % checked_domain)
                elif 'listen ' in line:
                    line = '    listen 80;'
                content.append(line)
            file_descriptor = StringIO.StringIO()
            file_descriptor.write('\n'.join(content))
            put(file_descriptor, file_path)
            _debug('Restarting nginx...')
            run('/etc/init.d/nginx restart')
    else:
        _debug('Creating nginx file %s...' % file_path)
        local_port = _available_port()
        if checked_domain:
            port = 80
            server_name = checked_domain
        else:
            port = local_port + 1000
            server_name = env.hosts[0]
        data = dict(project_name=project_name, server_name=server_name, port=port, local_port=local_port)
        text = NGINEX_FILE_CONTENT % data
        append(file_path, text)
        _debug(u'Nginx configured with %s:%s' % (server_name, port))
        _debug('Restarting nginx...')
        run('/etc/init.d/nginx restart')


def _setup_supervisor_file():
    file_path = '/etc/supervisor/conf.d/%s.conf ' % project_name
    _debug('Checking supervisor file %s...' % file_path)
    if not exists(file_path):
        _debug('Creating supervisor file %s...' % file_path)
        data = dict(project_name=project_name)
        text = SUPERVISOR_FILE_CONTENT % data
        append(file_path, text)
        _debug('Reloading supervisorctl...')
        run('supervisorctl reload')


def _setup_gunicorn_file():
    file_path = '/var/opt/%s/gunicorn_start.sh ' % project_name
    _debug('Checking gunicorn file %s...' % file_path)
    if not exists(file_path):
        _debug('Creating gunicorn file %s' % file_path)
        port = _available_port()
        data = dict(project_name=project_name, port=port)
        text = GUNICORN_FILE_CONTENT % data
        append(file_path, text)
        run('chmod a+x %s' % file_path)


def _setup_remote_webserver():
    _setup_nginx_file()
    _setup_supervisor_file()
    _setup_gunicorn_file()


def _reload_remote_application():
    _debug('Updating project in remote server...')
    with cd(remote_project_dir):
        virtual_env_dir = '/var/opt/.virtualenvs'
        with shell_env(WORKON_HOME=virtual_env_dir):
            run('source /usr/local/bin/virtualenvwrapper.sh && workon %s && python manage.py sync' % project_name)
            run('chown -R www-data.www-data .')
            run('chmod a+w *.db')
            run('ls -l')
            _debug('Restarting supervisorctl...')
            run('supervisorctl restart %s' % project_name)


def _delete_remote_project():
    _debug('Deleting remove project...')
    if exists(remote_project_dir):
        run('rm -r %s' % remote_project_dir)


def _delete_remote_env():
    _debug('Deleting remote env...')
    run('source /usr/local/bin/virtualenvwrapper.sh && rmvirtualenv %s' % project_name)


def _delete_domain():
    url = 'https://api.digitalocean.com/v2/domains'
    if settings.DIGITAL_OCEAN_DOMAIN:
        _debug('Deleting domain %s...' % settings.DIGITAL_OCEAN_DOMAIN)
        params = (settings.DIGITAL_OCEAN_TOKEN, url, settings.DIGITAL_OCEAN_DOMAIN)
        command = '''curl -X DELETE -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s/%s"''' % params
        local(command)


def _delete_repository():
    project_git_dir = '/home/git/%s.git' % project_name
    if exists(project_git_dir):
        run('rm -r %s' % project_git_dir)


def _delete_local_repository():
    _debug('Deleting local repository...')
    with cd(project_dir):
        local('rm -rf .git')


def _delete_nginx_file():
    _debug('Deleting nginx file...')
    file_path = '/etc/nginx/sites-enabled/%s ' % project_name
    if exists(file_path):
        run('rm %s' % file_path)


def _delete_supervisor_file():
    _debug('Deleting supervisor file..')
    file_path = '/etc/supervisor/conf.d/%s.conf ' % project_name
    if exists(file_path):
        run('rm %s' % file_path)


def _reload_remote_webserver():
    _debug('Reloading supervisorctl...')
    run('supervisorctl reload')
    _debug('Reloading nginx...')
    run('/etc/init.d/nginx restart')
    _debug('Starting supervisor...')
    run('service supervisor start')


def _configure_crontab():
    _debug('Configuring crontab...')
    output = run("crontab -l")
    line = '0 * * * * /var/opt/.virtualenvs/%s/bin/python /var/opt/%s/manage.py backup >/tmp/cron.log 2>&1' % (
    project_name, project_name)
    if line not in output:
        run('crontab -l | { cat; echo "%s"; } | crontab -' % line)


def _check_droplet():
    _check_local_keys()

    url = 'https://api.digitalocean.com/v2/droplets/'
    params = (settings.DIGITAL_OCEAN_TOKEN, url)
    command = '''curl -X GET -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s"''' % params
    _debug('Checking if droplet exists...')
    response = json.loads(local(command, capture=True))

    for droplet in response[u'droplets']:
        ip_address = droplet['networks']['v4'][0]['ip_address']
        if droplet['name'] == project_name or ip_address == settings.DIGITAL_OCEAN_SERVER:
            _debug('Droplet found with IP %s' % ip_address)
            local_home_dir = local('echo $HOME', capture=True)
            local_known_hosts_path = path.join(local_home_dir, '.ssh/known_hosts')
            _debug('Checking if file %s exists...' % local_known_hosts_path)
            if not os.path.exists(local_known_hosts_path):
                _debug('Creating empty file %s...' % local_known_hosts_path)
                local('touch %s' % local_known_hosts_path)
            local_known_hosts_file_content = open(local_known_hosts_path, 'r').read()
            if ip_address not in local_known_hosts_file_content:
                _debug('Registering %s as known host...' % ip_address)
                time.sleep(5)
                local('ssh-keyscan -T 15 %s >> %s' % (ip_address, local_known_hosts_path))
                if settings.DIGITAL_OCEAN_SERVER not in local_known_hosts_file_content:
                    _debug('Registering %s as known host...' % settings.DIGITAL_OCEAN_SERVER)
                    local('ssh-keyscan %s >> %s' % (settings.DIGITAL_OCEAN_SERVER, local_known_hosts_path))
            return ip_address

    _debug(u'No droplet cound be found for the project')


def _create_droplet():
    _check_local_keys()
    if settings.DIGITAL_OCEAN_TOKEN:
        url = 'https://api.digitalocean.com/v2/account/keys'
        params = (settings.DIGITAL_OCEAN_TOKEN, url)
        _debug('Getting installed keys at digital ocean...')
        command = '''curl -X GET -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s"''' % params
        response = json.loads(local(command, capture=True))
        # print response
        ssh_keys = []
        for ssh_key in response['ssh_keys']:
            ssh_keys.append(ssh_key['id'])

        _debug('Creating droplet...')
        url = 'https://api.digitalocean.com/v2/droplets/'
        params = settings.DIGITAL_OCEAN_TOKEN, project_name, 'nyc3', '512mb', 'debian-8-x64', ssh_keys, url
        command = '''curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' -d '{"name":"%s","region":"%s","size":"%s","image":"%s", "ssh_keys":%s}' "%s"''' % params
        response = json.loads(local(command, capture=True))
        droplet_id = response['droplet']['id']

        url = 'https://api.digitalocean.com/v2/droplets/%s/' % droplet_id
        params = (settings.DIGITAL_OCEAN_TOKEN, url)
        command = '''curl -X GET -H 'Content-Type: application/json' -H 'Authorization: Bearer %s' "%s"''' % params
        response = json.loads(local(command, capture=True))
        # print response
        ip_address = response['droplet']['networks']['v4'][0]['ip_address']
        _debug('Droplet created with IP %s!' % ip_address)
        _update_settings_file(ip_address)
        return _check_droplet()

    _debug(u'Please, set the DIGITAL_OCEAN_TOKEN value in settings.py file')
    sys.exit()


def _execute_aptget():
    with cd('/'):
        run('apt-get update')
        run('apt-get -y install build-essential python-dev python-pip git nginx supervisor libncurses5-dev')
        run('apt-get -y install vim')
        run(
            'apt-get -y install libjpeg62-turbo-dev libopenjpeg-dev libfreetype6-dev libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev libjpeg-dev')
        run('apt-get -y install htop')

        if not contains('/etc/security/limits.conf', '65536'):
            # print LIMITS_FILE_CONTENT
            append('/etc/security/limits.conf', LIMITS_FILE_CONTENT)

        run('pip install --upgrade pip')
        run('pip install virtualenv virtualenvwrapper')

        if not contains('/root/.bashrc', 'WORKON_HOME'):
            # print BASHRC_FILE_CONTENT
            append('/root/.bashrc', BASHRC_FILE_CONTENT)

        if not exists('/swap.img'):
            run('lsb_release -a')
            run('dd if=/dev/zero of=/swap.img bs=1024k count=2000')
            run('mkswap /swap.img')
            run('swapon /swap.img')
            run('echo "/swap.img    none    swap    sw    0    0" >> /etc/fstab')


def _update_settings_file(ip):
    _debug('Updating settings.py file with %s for DIGITAL_OCEAN_SERVER' % ip)
    settings_file_path = path.join(settings.BASE_DIR, '%s/settings.py' % project_name)
    content = []
    settings_file = open(settings_file_path)
    lines = settings_file.read().split(u'\n')
    settings_file.close()
    for line in lines:
        if u'DIGITAL_OCEAN_SERVER' in line:
            line = u'DIGITAL_OCEAN_SERVER = \'%s\'' % ip
        content.append(line)
    content_str = u'\n'.join(content)
    settings_file = open(settings_file_path, 'w')
    settings_file.write(content_str.encode('utf-8'))
    settings_file.close()


def backupdb():
    local_home_dir = local('echo $HOME', capture=True)
    backup_dir = os.path.join(local_home_dir, 'backup')
    if not os.path.exists(backup_dir):
        local('mkdir -p %s' % backup_dir)
    with cd('/var/opt'):
        for entry in run('ls').split():
            file_name = '/var/opt/%s/sqlite.db' % entry
            bakcup_file_name = os.path.join(backup_dir, '%s.db' % entry)
            if exists(file_name):
                command = 'scp %s@%s:%s %s' % (username, env.hosts[0], file_name, bakcup_file_name)
                local(command)


def deploy():
    _execute_aptget()
    _check_remote_keys()
    _setup_local_repository()
    _push_local_changes()
    _setup_remote_env()
    _setup_remote_repository()
    _setup_remote_project()
    _setup_remote_webserver()
    _reload_remote_application()
    _print_remote_url()


def update():
    _push_local_changes()
    _setup_remote_repository()
    _setup_remote_project()
    _reload_remote_application()
    _setup_nginx_file()
    _print_remote_url()


def push():
    _push_local_changes()
    _setup_remote_repository()
    _reload_remote_application()
    _print_remote_url()


def undeploy():
    _delete_remote_project()
    _delete_domain()
    _delete_repository()
    _delete_local_repository()
    _delete_nginx_file()
    _delete_supervisor_file()
    _reload_remote_webserver()
    _delete_remote_env()


if 'deploy' in sys.argv:
    if settings.DIGITAL_OCEAN_SERVER:
        env.hosts = [_check_droplet()]
    else:
        env.hosts = [_create_droplet()]
elif 'undeploy' in sys.argv or 'update' in sys.argv or 'push' in sys.argv:
    env.hosts = [_check_droplet()]
else:
    env.hosts = []




