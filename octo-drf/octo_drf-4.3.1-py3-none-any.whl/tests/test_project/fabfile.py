

from fabric.api import *


def push(message):
    local('git add ../../ .')
    local('git commit -m "{}"'.format(message))
    local('git push')


def update(message):
    push(message)
    local('pip install --no-deps git+ssh://git@gitlab.com/octoberweb/octo_drf_core.git@refactor --upgrade')


def make():
    local('python manage.py makemigrations')


def migrate():
    local('python manage.py migrate')