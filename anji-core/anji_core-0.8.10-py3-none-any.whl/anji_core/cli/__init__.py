import logging
import socket
from typing import List

import click
from repool_forked import ConnectionPool
import coloredlogs

from ..types import NodeType
from ..migrations import MIGRATION_ORDER
from .utils import AnjiConfig, EnumType
from .pid_control import AnjiPidBox, AnjiPidStock, AnjiSupervisor, bootstrap

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """
    Anji Platform
    """


@cli.command()
@click.option('--node-type', type=EnumType(NodeType), default=NodeType.master.name, help='Node type')  # pylint: disable=no-member
@click.option('--node-name', type=str, default='SingleNode', help='Node name')
def single(node_type: NodeType, node_name: str) -> None:
    """
    Single anji node for debugging
    """
    bootstrap(node_type, node_name, [])


@cli.command()
@click.option('--master', '-m', help='Master node name')
@click.option('--worker', '-w', multiple=True, help='Name of workers node')
@click.option('--cron', '-cr', multiple=True, help='Name of cron workers node')
@click.option('--libraries', '-l', multiple=True, help='Name of anji addon library to import', default=None)
@click.option('--system-analyze/--no-system-analyze', default=False, help='Enable or disable system analyze feature')
def node(master: str, worker: List[str], cron: List[str], libraries: List[str], system_analyze: bool) -> None:
    """
    Start powerful anji node
    """
    pid_stock = AnjiPidStock()
    if master:
        master_pidbox = AnjiPidBox(NodeType.master, master, libraries)
        pid_stock.add_bot_node(master_pidbox)
    for worker_name in worker:
        worker_pidbox = AnjiPidBox(NodeType.worker, worker_name, libraries)
        pid_stock.add_bot_node(worker_pidbox)
    for cron_name in cron:
        cron_pidbox = AnjiPidBox(NodeType.cron_worker, cron_name, libraries)
        pid_stock.add_bot_node(cron_pidbox)
    if system_analyze:
        pid_stock.add_bot_node(AnjiPidBox(NodeType.system_analyze, f'{socket.gethostname()} Checker', libraries))
    pid_stock.start_all()
    coloredlogs.install(logging.INFO, fmt=f'[%(asctime)s] (Supervisor) %(name)s:%(levelname)s: %(message)s')
    pid_stock.collect_node_info()
    supervisor = AnjiSupervisor(pid_stock)
    supervisor.start()


@cli.command()
def migrate():
    """
    Apply migrations to current rethinkdb instance
    """
    anji_config = AnjiConfig(NodeType.master, 'AnjiMigrateAgent')
    coloredlogs.install(logging.INFO, fmt='[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
    pool = ConnectionPool(
        db=anji_config.ANJI_RETHINK_DB,
        host=anji_config.ANJI_RETHINK_DB_HOST,
        port=anji_config.ANJI_RETHINK_DB_PORT,
        user=anji_config.ANJI_RETHINK_DB_USER,
        password=anji_config.ANJI_RETHINK_DB_PASSWORD,
    )
    for migration_version in MIGRATION_ORDER.keys():
        _log.info('Migrate to %s', migration_version)
        for migrate_function in MIGRATION_ORDER[migration_version]:
            _log.info(migrate_function.__doc__)
            migrate_function(pool, _log)
