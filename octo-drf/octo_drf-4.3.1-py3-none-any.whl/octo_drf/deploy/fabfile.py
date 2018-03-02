
import os

from src.settings.base import PROJECT_NAME
from fabric.api import *

PROJECT_NAME = PROJECT_NAME
ANSIBLE_PATH = os.environ.get('ANSIBLE_PATH')
DEV_PORT = 80
REPO = ''
PROD_HOST = ''
EXTRA_VARS = {}


def get_extra_vars(prod='false', branch='develop', host='dev', extra_vars=None):
    """
    Функция принимает создает дополнительный контекст для плейбуков ansible
    Разрешение контекста похоже на ansible.
    Контекст по возрастанию степени важности:

    default - который находится в этой функции
    extra - который находится в функциях вызывающий эту функцию
    EXTRA - на уровне модуля
    """
    if prod == 'true':
        branch = 'master'
        host = PROD_HOST

    default_extra_vars = {
        'project_name': PROJECT_NAME,
        '__host': host,
        'git_repo': REPO,
        'port_no': DEV_PORT,
        'git_branch': branch
    }
    if extra_vars:
        default_extra_vars.update(extra_vars)
    if EXTRA_VARS:
        default_extra_vars.update(EXTRA_VARS)
    return default_extra_vars


# REMOTE COMMANDS

def update_package_remote(prod='false', package_version='master', no_deps='false', package_upgrade='false'):
    package_dep = '--no-deps' if no_deps == 'true' else ''
    package_upgrade = '--upgrade' if package_upgrade == 'true' else ''
    package_vars = {
        'package_deps': package_dep,
        'package_version': package_version,
        'package_upgrade': package_upgrade,
    }
    extra_vars = get_extra_vars(prod, extra_vars=package_vars)
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/update_package.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


def initial_deploy(prod='false'):
    extra_vars = get_extra_vars(prod)
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/deploy/initial_deploy_dev.yml -e "{extra_vars}"'
    if prod == 'true':
        command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/deploy/initial_deploy_prod.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


def deploy_server(prod='false'):
    extra_vars = get_extra_vars(prod)
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/deploy/deploy_server.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


def deploy_client(prod='false'):
    extra_vars = get_extra_vars(prod)
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/deploy/deploy_client.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


# LOCAL COMMANDS
def create_db():
    extra_vars = get_extra_vars(host='localhost')
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/local/create_db.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


def update_package(package_version='master', no_deps='false', package_upgrade='false'):
    package_dep = '--no-deps' if no_deps == 'true' else ''
    package_upgrade = '--upgrade' if package_upgrade == 'true' else ''
    package_vars = {
        'package_deps': package_dep,
        'package_version': package_version,
        'package_upgrade': package_upgrade,
    }
    extra_vars = get_extra_vars(host='localhost', extra_vars=package_vars)
    command = 'ansible-playbook -i {path}/inventory/hosts {path}/playbooks/update_package.yml -e "{extra_vars}"'
    local(command.format(path=ANSIBLE_PATH, extra_vars=extra_vars))


def makemigrations(settings='dev'):
    local('python manage.py makemigrations --settings=src.settings.{}'.format(settings))


def migrate(settings='dev'):
    local('python manage.py migrate --settings=src.settings.{}'.format(settings))


def first_migrate(settings='dev'):
    local('python manage.py makemigrations thumbnail --settings=src.settings.settings.{}'.format(settings))
    local('python manage.py migrate thumbnail --settings=src.settings.settings.{}'.format(settings))
    local('python manage.py migrate --settings=src.settings.settings.{}'.format(settings))


def runserver(host='127.0.0.1', port='8000'):
    local(
        'python manage.py runserver {host}:{port} --settings=src.settings.dev'.format(host=host, port=port)
    )


def createsuperuser(settings='dev'):
    local(
        'python manage.py createsuperuser --settings=src.settings.{}'.format(settings)
    )


