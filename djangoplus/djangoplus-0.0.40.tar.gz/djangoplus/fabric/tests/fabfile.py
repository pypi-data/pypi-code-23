# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from fabric.api import *
from os import path

WORKSPACE_PATH = '/Users/breno/Documents/Workspace'
PYTHON_PATH = '/var/opt/.virtualenvs/djangoplus/bin/python'
PROJECT_NAMES = ['abstract', 'blackpoint', 'emprestimos', 'fabrica', 'financeiro', 'formulacao', 'gouveia', 'companies']
EMPTY_TEST_FILE_CONTENT = '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangoplus._test_admin.models import User
from djangoplus.test import TestCase
from django.conf import settings


class AppTestCase(TestCase):

    def test_app(self):

        User.objects.create_superuser('_test_admin', None, settings.DEFAULT_PASSWORD)

        self.login('_test_admin', settings.DEFAULT_PASSWORD)
'''


DOCKER_FILE_CONTENT = '''FROM {}

RUN apt-get update
RUN apt-get -y install python-pip build-essential python-dev libfreetype6-dev libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev libjpeg-dev ssh openssh-server dnsutils curl vim git
RUN apt-get -y install chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev
RUN wget https://github.com/ariya/phantomjs/releases/download/2.1.3/phantomjs -P /usr/bin/
'''


def _test_start_project():
    if path.exists('/tmp/xxx'):
        local('rm -r /tmp/xxx')
    with lcd('/tmp/'):
        local('{}/djangoplus/djangoplus/bin/startproject xxx'.format(WORKSPACE_PATH))
        with lcd('/tmp/xxx'):
            local('{} manage.py test'.format(PYTHON_PATH))
        with lcd('/tmp'):
            local('rm -r /tmp/xxx')


def _test_project():
    local('{} manage.py test'.format(PYTHON_PATH))


def _test_admin():
    local('{} manage.py test djangoplus.admin.tests.AdminTestCase'.format(PYTHON_PATH))


def _test_workspace():
    with lcd(WORKSPACE_PATH):
        for test_project_name in PROJECT_NAMES:
            with lcd(test_project_name):
                local('{} manage.py test'.format(PYTHON_PATH))
    with lcd(path.join(WORKSPACE_PATH, 'djangoplus/djangoplus-demos')):
        for test_project_name in ['petshop', 'loja', 'biblioteca']:
            with lcd(test_project_name):
                local('{} manage.py test'.format(PYTHON_PATH))


def _test_testcases_generation():
    test_file_path = '{}/emprestimos/emprestimos/tests.py'.format(WORKSPACE_PATH)
    test_file_content = open(test_file_path).read()
    open(test_file_path, 'w').write(EMPTY_TEST_FILE_CONTENT)
    with lcd('{}/emprestimos'.format(WORKSPACE_PATH)):
        local('python manage.py test --add')
    print open(test_file_path).read()
    open(test_file_path, 'w').write(test_file_content)


def _test_so_installation(so):
    docker_file = open('/tmp/Dockerfile', 'w')
    docker_file.write(DOCKER_FILE_CONTENT.format(so))
    docker_file.close()
    local('docker build -t djangoplus-{} /tmp'.format(so))
    #local('docker run djangoplus-{} pip install djangoplus && startproject xyz && cd xyz && python manage.py test djangoplus.admin.tests.AdminTestCase'.format(so))


def test_installation():
    # _test_so_instalation('debian')
    _test_so_installation('ubuntu')


def testall():
    _test_start_project()
    _test_admin()
    _test_workspace()