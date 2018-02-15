# -*- coding: utf-8 -*-
from fabric.api import *
from os import path

WORKSPACE_PATH = '/Users/breno/Documents/Workspace'
PYTHON_PATH = '/var/opt/.virtualenvs/djangoplus/bin/python'
PROJECT_NAMES = ['abstract', 'blackpoint', 'emprestimos', 'fabrica', 'financeiro', 'formulacao', 'gouveia', 'companies']
EMPTY_TEST_FILE_CONTENT = '''# -*- coding: utf-8 -*-
from djangoplus._test_admin.models import User
from djangoplus.test import TestCase
from django.conf import settings


class AppTestCase(TestCase):

    def test_app(self):

        User.objects.create_superuser('_test_admin', None, settings.DEFAULT_PASSWORD)

        self.login(u'_test_admin', settings.DEFAULT_PASSWORD)
'''


def _test_start_project():
    if path.exists('/tmp/xxx'):
        local('rm -r /tmp/xxx')
    with lcd('/tmp/'):
        local('%s/djangoplus/djangoplus/bin/startproject xxx' % WORKSPACE_PATH)
        with lcd('/tmp/xxx'):
            local('%s manage.py test' % PYTHON_PATH)
        with lcd('/tmp'):
            local('rm -r /tmp/xxx')


def _test_project():
    local('%s manage.py test' % PYTHON_PATH)


def _test_admin():
    local('%s manage.py test djangoplus.admin.tests.AdminTestCase' % PYTHON_PATH)


def _test_workspace():
    with lcd(WORKSPACE_PATH):
        for test_project_name in PROJECT_NAMES:
            with lcd(test_project_name):
                local('%s manage.py test' % PYTHON_PATH)


def _test_testcases_generation():
    test_file_path = '%s/emprestimos/emprestimos/tests.py' % WORKSPACE_PATH
    test_file_content = open(test_file_path).read()
    open(test_file_path, 'w').write(EMPTY_TEST_FILE_CONTENT)
    with lcd('%s/emprestimos' % WORKSPACE_PATH):
        local('python manage.py test --add')
    print open(test_file_path).read()
    open(test_file_path, 'w').write(test_file_content)


def testall():
    _test_start_project()
    _test_admin()
    _test_workspace()