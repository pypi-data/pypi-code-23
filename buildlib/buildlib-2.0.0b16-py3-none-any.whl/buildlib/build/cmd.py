"""
Misc build commands.
Everything that does not deserve it's own package goes here.
"""

import os
import shutil
import glob
import subprocess as sp
from buildlib import yaml, module
from cmdi import command, CmdResult, CustomCmdResult


@command
def update_version_num_in_cfg(
    config_file: str,
    semver_num: str,
    **cmdargs,
) -> CmdResult:
    """
    Check if version num from proj-cfg is valid.
    Increase version num based on user input or ask user for a new version number.
    """

    cfg: dict = yaml.loadfile(
        config_file,
        keep_order=True
    )

    cfg.update({'version': semver_num})

    yaml.savefile(cfg, config_file)

    return semver_num


@command
def push_python_wheel_to_gemfury(
    wheel_file: str,
    **cmdargs,
) -> CmdResult:
    """"""
    sp.run(
        ['fury', 'push', wheel_file],
        check=True
    )


def _clean_bdist_tmp_files() -> None:
    """"""
    build_dir: str = f'{os.getcwd()}/build'
    egg_file: list = glob.glob('**.egg-info')
    egg_file: str = egg_file and egg_file[0] or ''

    os.path.isdir(build_dir) and shutil.rmtree(build_dir)
    os.path.isdir(egg_file) and shutil.rmtree(egg_file)


@command
def push_python_wheel_to_pypi(
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """"""
    sp.run(
        ['python', 'setup.py', 'bdist_wheel', 'upload', '-r', 'pypi'],
        check=True,
    )

    if clean_dir:
        _clean_bdist_tmp_files()


@command
def build_python_wheel(
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """
    Build python wheel for deployment, if it does not exists already.
    @clean_dir: Clean 'build' dir before running build command. This may be necessary because of
    this: https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up
    """
    sp.run(
        ['python', 'setup.py', 'bdist_wheel'],
        check=True,
    )

    if clean_dir:
        _clean_bdist_tmp_files()


@command
def inject_interface_txt_into_readme_md(
    interface_file: str,
    readme_file: str = 'README.md',
    **cmdargs,
) -> CmdResult:
    """
    Add content of help.txt into README.md
    Content of help.txt will be placed into the first code block (```) of README.md.
    If no code block is found, a new one will be added to the beginning of README.md.
    """
    readme_str: str = open(readme_file, 'r').read()
    interface_str = open(interface_file, 'r').read()

    help_str: str = f'```\n{interface_str}\n```'

    start: int = readme_str.find('```') + 3
    end: int = readme_str.find('```', start)

    if '```' in readme_str:
        mod_str: str = readme_str[0:start - 3] + help_str + readme_str[end + 3:]
    else:
        mod_str: str = help_str + readme_str

    with open('README.md', 'w') as modified_readme:
        modified_readme.write(mod_str)


@command
def run_build_file(
    build_file: str,
    **cmdargs,
) -> CmdResult:
    """
    === DEPRECATED ===
    In favor of the new build design, that includes 'makefile'.
    ==================
    """
    build_module = module.load_module_from_file(build_file)
    build_module.execute()

    # Add empty line
    print('\n')


@command
def build_read_the_docs(
    clean_dir: bool = False,
    **cmdargs,
) -> CmdResult:
    """"""
    build_dir = f'{os.getcwd()}/docs/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    sp.run(
        ['make', 'html'],
        cwd='{}/docs'.format(os.getcwd()),
        check=True,
    )


@command
def create_py_venv(
    py_bin: str,
    venv_dir: str,
    **cmdargs,
) -> CmdResult:
    """
    === DEPRECATED ===
    Use 'pipenv' instead.
    ==================

    @interpreter: must be the exact interpreter name. E.g. 'python3.5'
    """
    sp.run(
        [py_bin, '-m', 'venv', venv_dir],
        check=True,
    )


@command
def create_autoenv(
    venv_dir: str,
    **cmdargs,
) -> CmdResult:
    """
    === DEPRECATED ===
    Use 'pipenv' instead.
    ==================

    Create autoenv for automatic activation of virtual env when cd into dir.
    """
    venv_dir = os.path.normpath(venv_dir)
    venv_parent_dir: str = os.path.dirname(venv_dir)
    env_file_path: str = '{}/.env'.format(venv_parent_dir)

    with open(env_file_path, 'w+') as f:
        f.write('source {}/bin/activate\n'.format(venv_dir))
