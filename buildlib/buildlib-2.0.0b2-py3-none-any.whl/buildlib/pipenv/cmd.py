from processy import run, CompletedProcess
from cmdi import command, CmdResult, CustomCmdResult


@command
def install(
    dev: bool = False
) -> CmdResult:
    """
    Install packages from Pipfile.
    """
    dev_flag = ['--dev'] if dev else []
    p: CompletedProcess = run(['pipenv', 'install'] + dev_flag)


@command
def create_env(
    version: str
) -> CmdResult:
    """
    Create a fresh python environment.
    @version: E.g.: '3.6'
    """
    p: CompletedProcess = run(['pipenv', f'--python {version}'])
