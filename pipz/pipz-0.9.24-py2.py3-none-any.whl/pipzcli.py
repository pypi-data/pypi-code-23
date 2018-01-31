import click
import os
import zipfile
from pipz.pipzlib import install_private_package, download_private_package, install_powershell_module, isAdmin


@click.group()
@click.option('--admin/--no-admin', default=True)
@click.pass_context
def cli(ctx, admin):
    if admin and not isAdmin():
        raise Exception('Run the command with elevated priviledges.')

@cli.command(name='install')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install(ctx, package, secret):
    install_private_package(package, secret)


@cli.command(name='install-module')
@click.argument('package')
@click.option('--secret', default=None)
@click.pass_context
def install_module(ctx, package, secret):
    install_powershell_module(package, secret)

@cli.command(name='install-requirements')
@click.argument('package')
@click.pass_context
def install_requirements(ctx, package):
    file = os.path.join(os.path.dirname(__import__(package).__file__), 'z-requirements.py')
    if not os.path.exists(file):
        return
    if os.path.exists(file):
        with open(file) as fp:
            for cnt, line in enumerate(fp):
                line = line[1:].strip()
                if line.startswith('run '):
                    ll = line[len('run '):]
                    os.system(ll)
                    continue

                if len(line) == 0 or line.startswith('#') or line.startswith(';'):
                    continue
                try:
                    package, secret = [x.strip() for x in line.split('--secret')]

                    if package.startswith('module:'):
                        module = package[len('module:'):].strip()
                        install_powershell_module(module, secret)
                    else:
                        install_private_package(package, secret)
                except Exception as e:
                    print("Error installing: {}".format(line))
                    print(e)
        return

    print('{} does not exist.'.format(file))


@cli.command(name='uninstall')
@click.argument('package')
@click.pass_context
def uninstall(ctx, package):
    os.system('pip uninstall {}'.format(package))


@cli.command(name='download')
@click.argument('package')
@click.option('--secret', default=None)
@click.option('--unzip', default=False)
@click.pass_context
def download(ctx, package, secret, unzip):
    download_private_package(package, secret)
    if unzip:
        print('Unzip is not supported your. Please unzip the file manually')


if __name__ == '__main__':
    cli(obj={})
