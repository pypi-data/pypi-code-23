from fabsetup.fabutils import print_msg, run, subtask, suggest_localhost, task

from fabsetup_theno_termdown.fabutils import install_file
from fabsetup_theno_termdown.fabutils import install_user_command
from fabsetup_theno_termdown._version import __version__


@subtask
def install_pip_package():
    run('pip install --user termdown')


@subtask
def install_command():
    install_user_command('termdown',
                         TIMER_FINISHED_MESSAGE='TIMER FINISHED')


@subtask
def show_termdown_usage():
    print('termdown is now installed\n')
    print_msg('    python -m termdown --help\n')
    print('for example: time a pomodoro session\n')
    print_msg('    termdown 25m')


@task
@suggest_localhost
def termdown():
    '''Install or update termdown.

    Termdown (https://github.com/trehn/termdown) is a
    "[c]ountdown timer and stopwatch in your terminal".

    It installs termdown via `pip install --user termdown`.  Also, it installs a
    bash-wrapper script at `~/bin/termdown` which is convenient to time pomodoro
    sessions and pops up a notification when the timer finishes.

    Touched files, dirs, and installed packages:

        ~/bin/termdown
        pip-package termdown (`--user` install)
    '''
    install_pip_package()
    install_command()
    show_termdown_usage()
