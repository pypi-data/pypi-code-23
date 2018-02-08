#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging
import sys
import click
import errno
import os
from mali_commands.legit.config import default_missing_link_folder
from mali_commands.legit.context import init_context
from mali_commands.legit.gcs_utils import NonRetryException
from self_update.sdk_version import get_version, get_keywords
import click_completion

__prev_resolve_ctx = click_completion.resolve_ctx


def __mali_resolve_ctx(cli, prog_name, args):
    def find_top_parent_ctx(current_ctx):
        parent = current_ctx
        while True:
            if current_ctx.parent is None:
                break

            parent = current_ctx.parent
            current_ctx = parent

        return parent

    ctx = __prev_resolve_ctx(cli, prog_name, args)

    top_ctx = find_top_parent_ctx(ctx)

    init_context(
        ctx,
        top_ctx.params.get('outputformat'),
        top_ctx.params.get('configprefix'),
        top_ctx.params.get('configfile'))

    return ctx


click_completion.resolve_ctx = __mali_resolve_ctx
click_completion.init()

package = 'mali'


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], color=True)


def print_banner():
    from pyfiglet import figlet_format
    from termcolor import cprint
    from colorama import init

    init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected

    current_version = get_version(package)

    cprint(figlet_format('MALI   %s' % current_version, font='big'), 'yellow')


def _setup_logger(log_level):
    if not log_level:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging_method = getattr(root_logger, log_level.lower())
    logging_method('log level set to %s (this is a test message)', log_level)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--outputFormat', '-o', type=click.Choice(['tables', 'json', 'csv']), default='tables', required=False)
@click.option('--configPrefix', '-cp', envvar='CONFIG_PREFIX', required=False)
@click.option('--configFile', '-cf', envvar='CONFIG_FILE', required=False)
@click.option('--logLevel', envvar='LOG_LEVEL', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']), required=False)
@click.pass_context
def cli(ctx, outputformat, configprefix, configfile, loglevel):
    _setup_logger(loglevel)

    init_context(ctx, outputformat, configprefix, configfile)


@cli.command()
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.shells))
def install(shell):
    """Install the click-completion-command completion"""
    from mali_commands.install import rc_updater

    shell = shell or click_completion.get_auto_shell()

    code = click_completion.get_code(shell)

    file_name = '{dir}/completion.{shell}.inc'.format(dir=default_missing_link_folder(), shell=shell)

    def makedir():
        try:
            os.makedirs(os.path.dirname(file_name))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    makedir()

    with open(file_name, 'w') as f:
        f.write(code)

    rc_updater(shell, file_name)


@cli.command('version')
@click.pass_context
def version(ctx):
    current_version = get_version(package)

    print_banner()

    click.echo('%s %s' % (package, current_version))


# noinspection PyBroadException
def update_sdk(latest_version, user_path, throw_exception):
    from self_update.pip_util import pip_install, get_pip_server

    keywords = get_keywords(package) or []

    require_package = '%s==%s' % (package, latest_version)
    p, args = pip_install(get_pip_server(keywords), require_package, user_path)

    if p is None:
        return False

    try:
        std_output, std_err = p.communicate()
    except Exception:
        if throw_exception:
            raise

        logging.exception("%s failed", " ".join(args))
        return False

    rc = p.returncode

    if rc != 0:
        logging.error('%s failed to upgrade to latest version (%s)', package, latest_version)
        logging.error("failed to run %s (%s)\n%s\n%s", " ".join(args), rc, std_err, std_output)
        return False

    logging.info('%s updated to latest version (%s)', package, latest_version)

    return True


def self_update(throw_exception=False):
    from self_update.pip_util import get_latest_pip_version

    current_version = get_version(package)
    keywords = get_keywords(package) or []

    if current_version is None:
        return

    latest_version = get_latest_pip_version(package, keywords, throw_exception=throw_exception)

    if latest_version is None:
        return

    if current_version == latest_version:
        return

    running_under_virtualenv = getattr(sys, 'real_prefix', None) is not None

    if not running_under_virtualenv:
        logging.info('updating %s to version %s in user path', package, latest_version)

    return update_sdk(latest_version, user_path=not running_under_virtualenv, throw_exception=throw_exception)


def add_commands():
    from mali_commands import auth_commands, projects_commands, orgs_commands, experiments_commands, code_commands, \
        models_commands, data_commands

    cli.add_command(auth_commands)
    cli.add_command(projects_commands)
    cli.add_command(orgs_commands)
    cli.add_command(experiments_commands)
    cli.add_command(code_commands)
    cli.add_command(models_commands)
    cli.add_command(data_commands)


def main():
    import os

    if os.environ.get('MISSINGLINKAI_ENABLE_SELF_UPDATE'):
        self_update()

    add_commands()
    cli()


if __name__ == "__main__":
    try:
        main()
    except NonRetryException as ex:
        pass
