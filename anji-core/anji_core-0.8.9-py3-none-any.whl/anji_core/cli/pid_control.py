from multiprocessing import Process
from multiprocessing.connection import Pipe, Connection
import logging
from typing import List, Dict
import asyncio
import importlib

from errbot.bootstrap import setup_bot
from repool_forked import ConnectionPool
import rethinkdb as R

from ..types import NodeType, InternalMessageState
from ..backend import AnjiBackendMixin
from ..internal import InternalMessage
from .utils import AnjiConfig

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['AnjiPidBox', 'AnjiPidStock', 'AnjiSupervisor', 'bootstrap']

_log = logging.getLogger(__name__)


def bootstrap(node_type: NodeType, bot_name: str, libraries: List[str], multiprocess_connection: Connection = None) -> None:
    from errbot.logs import root_logger
    anji_config = AnjiConfig(node_type, bot_name)
    if libraries is not None:
        for library in libraries:
            _log.info('Preload library %s', library)
            importlib.import_module(library)
    _log.info('Use backend %s', anji_config.BACKEND)
    bot: AnjiBackendMixin = setup_bot(anji_config.BACKEND, root_logger, anji_config)
    if multiprocess_connection is not None:
        bot.multiprocess_mode(multiprocess_connection)
        bot.supervisor_connection.send(bot.uuid)
    bot.log_config()
    if node_type == NodeType.master:
        bot.serve_forever()
    elif node_type == NodeType.worker:
        bot.serve_forever_function(bot.serve_worker)
    elif node_type == NodeType.cron_worker:
        bot.serve_forever_function(bot.serve_cron_worker)
    elif node_type == NodeType.system_analyze:
        bot.serve_forever_function(bot.serve_system_analyze)


class AnjiPidBox:

    __slots__ = ['process', 'child_pipe', 'parent_pipe', 'node_type', 'bot_name']

    def __init__(self, node_type: NodeType, bot_name: str, libraries: List[str]) -> None:
        self.node_type: str = node_type
        self.bot_name: str = bot_name
        parent_pipe, child_pipe = Pipe()
        self.parent_pipe: Connection = parent_pipe
        self.child_pipe: Connection = child_pipe
        self.process: Process = Process(target=bootstrap, args=(node_type, bot_name, libraries), kwargs=dict(multiprocess_connection=self.child_pipe))

    def start(self) -> None:
        self.process.start()


class AnjiPidStock:

    __slots__ = ['dict_by_type', 'dict_by_name', 'dict_by_uuid']

    def __init__(self) -> None:
        self.dict_by_type: Dict[NodeType, List[AnjiPidBox]] = {}
        self.dict_by_name: Dict[str, AnjiPidBox] = {}
        self.dict_by_uuid: Dict[str, AnjiPidBox] = {}

    def add_bot_node(self, pid_box: AnjiPidBox) -> None:
        self.dict_by_type.setdefault(pid_box.node_type, []).append(pid_box)
        self.dict_by_name[pid_box.bot_name] = pid_box

    def start_all(self) -> None:
        for pid_box in self.dict_by_name.values():
            pid_box.start()

    def collect_node_info(self) -> None:
        for pid_box in self.dict_by_name.values():
            _log.info('Collect information about %s', pid_box.bot_name)
            pid_box.parent_pipe.poll(None)
            uuid = pid_box.parent_pipe.recv()
            _log.info('%s node uuid is %s', pid_box.bot_name, uuid)
            self.dict_by_uuid[uuid] = pid_box


class AnjiSupervisor:

    __slots__ = ['pid_stock', 'pool']

    def __init__(self, pid_stock: AnjiPidStock) -> None:
        self.pid_stock = pid_stock
        anji_config = AnjiConfig(NodeType.master, 'AnjiSupervisor')
        self.pool = ConnectionPool(
            db=anji_config.ANJI_RETHINK_DB,
            host=anji_config.ANJI_RETHINK_DB_HOST,
            port=anji_config.ANJI_RETHINK_DB_PORT,
            user=anji_config.ANJI_RETHINK_DB_USER,
            password=anji_config.ANJI_RETHINK_DB_PASSWORD,
        )

    async def listen_messages(self) -> None:
        connection = await R.connect(**self.pool._conn_args)
        query = R.table(InternalMessage._table).get_all(InternalMessageState.posted.name, index='state')  # pylint: disable=no-member
        feed = await query.changes(include_types=True, include_initial=True).run(connection)
        while await feed.fetch_next():
            change = await feed.next()
            if change['type'] not in ['add', 'initial']:
                continue
            message = InternalMessage(id_=change['new_val']['id'])
            message.load(rethink_dict=change['new_val'])
            self.allocate_message(message)

    def allocate_message(self, message: InternalMessage) -> None:
        _log.info('Process internal message %s with type %s', message.message, message.type)
        if NodeType.search(message.target_indentifier):
            targets = self.pid_stock.dict_by_type.get(NodeType.master)
            if targets:
                _log.info('Delivery task to node %s', targets[0].bot_name)
                targets[0].parent_pipe.send(message)
        else:
            target = self.pid_stock.dict_by_name.get(message.target_indentifier)
            if target:
                _log.info('Delivery task to node %s', target.bot_name)
                target.parent_pipe.send(message)

    async def healty_check(self) -> None:
        while True:
            for name, pid_box in self.pid_stock.dict_by_name.items():
                if not pid_box.process.is_alive():
                    _log.warning('Node %s was down', name)
                else:
                    _log.info('Node %s is alive', name)
            await asyncio.sleep(30)

    def start(self) -> None:
        R.set_loop_type('asyncio')
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        loop.run_until_complete(self.listen_messages())
        loop.run_until_complete(self.healty_check())
        loop.run_forever()
