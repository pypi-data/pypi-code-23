#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: /finit.py
@time: 18-1-23 上午12:19
"""

import os
import click
import getpass
import subprocess


class Project(object):

    def __init__(self, pname, ppath, simple):
        self.pname = pname
        self.ppath = ppath
        self.simple = simple

    def repo(self):
        if os.path.exists(self.ppath):
            print("{} exist.".format(self.ppath))
            return False
        print("{} will create.".format(self.ppath))
        try:
            os.mkdir(self.ppath)
        except OSError:
            # print("{} will create.".format(self.ppath))
            os.makedirs(self.ppath)
        return True

    def pyenv(self, envpath, pythonv='python3'):
        if os.path.exists(envpath):
            return False
        try:
            os.mkdir(envpath)
        except OSError:
            os.makedirs(envpath)
        # virtualenv -p python3  ./test
        try:
            exec_cmd = subprocess.check_output(['virtualenv', '-p', pythonv, envpath])
        except subprocess.CalledProcessError as e:
            err_info = e.output
            err_code = e.returncode
            print('exec error:{}/{}'.format(err_info, err_code))
            return False
        print(exec_cmd.decode('utf-8'))
        return True

    def do_simple(self):
        simple_py = '''
#!/usr/bin/env python3
# coding=utf-8


from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()

        '''
        with open(os.path.join(self.ppath, self.pname+'.py'), 'w') as f:
            print(simple_py)
            f.write(simple_py)
            print("done")
        return True

    def init(self):
        if self.simple:
            self.do_simple()
        else:
            # Todo
            print("pass")


@click.group()
def cli():
    """A simple cmd line tool"""


@click.command(help='create new project')
@click.argument('project_name')
@click.option('--path', default="ysbot/repo/", help="project path")
@click.option('--envpath', default="ysbot/pypi/", help="project venv path")
@click.option('--simple', is_flag=True, default=True, help="default simple")
def new(project_name, path, envpath, simple):
    user = getpass.getuser()
    if path.startswith("ysbot"):
        path = '/' + user + '/' + path
    if envpath.startswith("ysbot"):
        envpath = '/' + user + '/' + envpath
    project_path = os.path.join(path, project_name)
    project_envpath = os.path.join(envpath, project_name)
    repo = Project(project_name, project_path, simple)
    if repo.repo():
        if repo.pyenv(project_envpath):
            click.echo("create project {} successful".format(project_name))
            repo.init()
            click.echo("init project")
    click.echo("Maybe Error, Hehe.")

cli.add_command(new)
