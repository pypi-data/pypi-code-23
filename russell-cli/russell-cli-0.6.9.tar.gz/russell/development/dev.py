# coding=utf-8
import click

import russell
from russell.log import configure_logger
from russell.main import check_cli_version, add_commands, print_version
from russell.cli.project import clone2
from russell.cli.data import *
from russell.cli.data import _upload
from russell.log import configure_logger
from russell.manager.auth_config import AuthConfigManager
from russell.manager.data_config import DataConfigManager
from russell.manager.experiment_config import ExperimentConfigManager

# is_eager=True 表明该命令行选项优先级高于其他选项；
# expose_value=False 表示如果没有输入该命令行选项，会执行既定的命令行流程；
# callback 指定了输入该命令行选项时，要跳转执行的函数；

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version info")
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(verbose):
    """
    Russell CLI interacts with Russell server and executes your commands.
    More help is available under each command listed below.
    """
    russell.russell_host = "http://test.dl.russellcloud.com"
    russell.russell_web_host = "http://test.russellcloud.com"
    russell.russell_proxy_host = "https://dev.russellcloud.com:8000"
    russell.russell_fs_host = "test.fs.russellcloud.com"
    russell.russell_fs_port = 8081
    AuthConfigManager.CONFIG_FILE_PATH += "-dev"
    DataConfigManager.CONFIG_FILE_PATH += "-dev"
    ExperimentConfigManager.CONFIG_FILE_PATH += "-dev"
    configure_logger(verbose)
    check_cli_version()

add_commands(cli)

data.add_command(_upload)
cli.add_command(clone2)
cli.add_command(data)
