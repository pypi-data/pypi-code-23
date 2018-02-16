from cmdi import command, CmdResult, CustomCmdResult
import subprocess as sp


@command
def install(
    dev: bool = False
) -> CmdResult:
    """
    Install packages from Pipfile.
    """
    dev_flag = ['--dev'] if dev else []
    sp.run(
        ['pipenv', 'install'] + dev_flag,
        check=True,
    )


@command
def create_env(
    version: str
) -> CmdResult:
    """
    Create a fresh python environment.
    @version: E.g.: '3.6'
    """
    sp.run(
        ['pipenv', f'--python {version}'],
        check=True,
    )
