import sys
import os
from pybuilder.core import task, depends, init
from pybuilder.utils import execute_command


class PybResearchException(Exception):
    pass


def copy_env(target_dir):
    env = dict(os.environ)
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] += os.pathsep + target_dir
    else:
        env['PYTHONPATH'] = target_dir
    return env


@init
def initialize_research_tools(project):
    project.set_property('use_seaborn', True)
    project.set_property('new_figure_name', 'figure.py')


@task('run_script', description='run script $PYB_SCRIPT in package context')
@depends('package')
def run_script(project, logger):
    scripts_directory = project.get_property('dir_dist_scripts')
    target_dir = project.expand_path('$dir_dist')
    target_script = os.getenv('PYB_SCRIPT')
    logger.info('Executing script %s in package context', target_script)
    env = copy_env(target_dir)
    logger.debug('Using environment:\n%s', env)
    if target_script:
        command = '{} {}'.format(
            sys.executable,
            os.path.join(target_dir, scripts_directory, target_script))
        if execute_command(command, env=env, shell=True):
            raise PybResearchException('Script failed')
    else:
        logger.error('PYB_SCRIPT variable is not set')
        raise PybResearchException('No PYB_SCRIPT variable set')


@task('start_figure',
      description='create figure template figure.py in scripts folder')
def start_figure(project, logger):
    scripts_directory = project.get_property('dir_dist_scripts')
    new_figure_name = project.get_property('new_figure_name')
    figure_content = [
        'import pylab as pl',
        'import seaborn as sns',
        'import __main__ as main',
        'from os.path import basename',
        '',
        'import matplotlib.gridspec as gridspec',
        '',
        "if __name__ == '__main__':"
        "    sns.set_style('ticks')",
        "    sns.set_palette('colorblind')",
        '',
        '    gs = gridspec.Gridspec(1, 1)  # might be other layout',
        '',
        '    # Your figure code here',
        '    ax = pl.subplot(gs[0, 0])  # to create subplots',
        '',
        '    pl.tight_layout()',
        '    sns.despine()',
        '    pl.savefig(basename(main.__file__) + ".svg")',
        '    pl.show()',
    ]
    if not project.get_property('use_seaborn'):
        figure_content = [line for line in figure_content if 'sns' not in line]
    target_file = os.path.join(scripts_directory, new_figure_name)
    if os.path.exists(target_file):
        msg = 'Figure script {} exists'.format(target_file)
        logger.error(msg)
        raise PybResearchException(msg)
    else:
        with open(target_file, 'w') as f:
            f.write('\n'.join(figure_content))
