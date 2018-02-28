# *- coding: utf-8 -*- 
"""click API for NgoProject"""
import click
import gettext

from ngoproject._project import Project
from ngoproject._environment import ToxEnvironment

_ = gettext.gettext

######################
# CLASSES ENTRY POINTS
######################

# CLASS Project
@click.group()
@click.option('--name')
@click.pass_context
def project(ctx,name):
    """  """
    ctx.obj = Project()
    click.echo('Project %r' % ctx.obj)


# METHOD create_click of CLASS Project
@project.command()
@click.pass_context
def create_click():
    """ create the api for click """
    click.echo('create_click')
    ctx.obj.create_click()

# METHOD create_pypirc of CLASS Project
@project.command()
@click.option('--username')
@click.option('--password')
@click.pass_context
def create_pypirc(username, password):
    """ create .pypirc file containing pypi identifiers """
    click.echo('create_pypirc')
    ctx.obj.create_pypirc()

# METHOD publish of CLASS Project
@project.command()
@click.option('--server')
@click.pass_context
def publish(server):
    """ publish python project on pypi """
    click.echo('publish')
    ctx.obj.publish()

# METHOD clean_imports of CLASS Project
@project.command()
@click.pass_context
def clean_imports():
    """ execute ISORT and autoflake to clean imports in source files """
    click.echo('clean_imports')
    ctx.obj.clean_imports()

# METHOD build of CLASS Project
@project.command()
@click.pass_context
def build():
    """ build the project according to tox.ini or premake """
    click.echo('build')
    ctx.obj.build()

# METHOD create_file of CLASS Project
@project.command()
@click.argument('filetype')
@click.argument('name')
@click.pass_context
def create_file(filetype, name):
    """ create a new file with a given template """
    click.echo('create_file')
    ctx.obj.create_file()

# METHOD premake5 of CLASS Project
@project.command()
@click.option('--target', default='gmake')
@click.pass_context
def premake5(target):
    """ execute premake4 """
    click.echo('premake5')
    ctx.obj.premake5()

# METHOD format_code of CLASS Project
@project.command()
@click.pass_context
def format_code():
    """ execute YAPF to clean imports in source files """
    click.echo('format_code')
    ctx.obj.format_code()

# METHOD futurize of CLASS Project
@project.command()
@click.option('--stage', help=_('1 safe fixes, 2 py3 style wrapped for py2, 0 both'))
@click.pass_context
def futurize(stage):
    """ execute futurize with input stage 
    unicode by default,"""
    click.echo('futurize')
    ctx.obj.futurize()

# METHOD py23 of CLASS Project
@project.command()
@click.pass_context
def py23():
    """ execute futurize, clean_imports and format_code """
    click.echo('py23')
    ctx.obj.py23()

# METHOD create_apipkg of CLASS Project
@project.command()
@click.pass_context
def create_apipkg():
    """ create the namespace for apipkg """
    click.echo('create_apipkg')
    ctx.obj.create_apipkg()

# METHOD docker of CLASS Project
@project.command()
@click.pass_context
def docker():
    """ execute a list of commands on a docker container 
    the default image is "numengo/build-x64" but can be changed with options['dockerimage']"""
    click.echo('docker')
    ctx.obj.docker()

# METHOD premake4 of CLASS Project
@project.command()
@click.option('--target', default='gmake')
@click.pass_context
def premake4(target):
    """ execute premake4 """
    click.echo('premake4')
    ctx.obj.premake4()

# CLASS ToxEnvironment
@click.group()
@click.pass_context
def project_tox(ctx,):
    """  """
    ctx.obj = ToxEnvironment()
    click.echo('ToxEnvironment %r' % ctx.obj)


# METHOD list_env of CLASS ToxEnvironment
@project_tox.command()
@click.option('--all')
@click.pass_context
def list_env(all):
    """  """
    click.echo('list_env')
    ctx.obj.list_env()


