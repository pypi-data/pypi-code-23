import subprocess


def run_shell(cmd: str) -> str:
    """
    Runs a command in the shell, waits for it to complete,
    then returns the output

    :param (str) cmd: shell command to be executed
    :return: (str)

    Usage::

        >>> run_shell('ls | grep Doc')
        'Documents'
    """
    return subprocess.getoutput(cmd)
