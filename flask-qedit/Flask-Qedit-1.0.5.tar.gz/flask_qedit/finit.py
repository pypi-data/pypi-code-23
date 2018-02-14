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
import subprocess


class Project(object):

    def __init__(self, pname, ppath, simple):
        self.pname = pname
        self.ppath = ppath
        self.simple = simple

    def repo(self):
        if os.path.exists(self.ppath):
            return False

        os.mkdir(self.ppath)
        return True

    def pyenv(self, envpath, pythonv='python3'):
        if os.path.exists(envpath):
            return False
        os.mkdir(envpath)
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
            f.write(simple_py)
        return True

    def init(self):
        if self.simple:
            self.do_simple()
        else:
            # Todo
            print("pass")
        return True


@click.group()
def cli():
    """A simple cmd line tool"""


@click.command(help='create new project')
@click.argument('project_name')
@click.option('--path', default="~/ysbot/repo/")
@click.option('--envpath', default="~/ysbot/pypi")
@click.option('--simple', is_flag=True)
def new(project_name, path, envpath, simple):
    project_path = os.path.join(path, project_name)
    project_envpath = os.path.join(path, envpath)
    repo = Project(project_name, project_path, simple)
    if repo.repo():
        if repo.pyenv(project_envpath):
            click.echo("create project {} successful".format(project_name))
            return
    click.echo("Maybe Error, Hehe.")

cli.add_command(new)