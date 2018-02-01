import logging

from anji_orm import Model, StringField, register, EnumField
import rethinkdb as R

from .nodes import NodeManager
from .types import InternalMessageType, InternalMessageState, NodeType, CronWorkerCommandType

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)
INTERNAL_BUS_LABEL = 'from_internal_bus'


class InternalMessage(Model):

    _table = 'internal_message'

    message = StringField()
    state = EnumField(InternalMessageState, secondary_index=True)
    type = EnumField(InternalMessageType, secondary_index=True)
    source_user_technical_name = StringField()
    target_indentifier = StringField(default='*')

    def consume(self) -> bool:
        with register.pool.connect() as conn:
            result = self.table.get(self.id).update(
                R.branch(
                    R.row['state'] == InternalMessageState.posted.value,
                    {"state": InternalMessageState.consumed.value},
                    None
                )
            ).run(conn)
            if not result.get("replaced"):
                _log.debug('Message %s already consumed by another node, skip.', self.id)
                return False
            self.state = InternalMessageState.consumed
        return True


class InternalBus:

    def post_fake_message(self, message: str, source_user_technical_name: str = '') -> InternalMessage:
        message_record = InternalMessage(
            message=message,
            state=InternalMessageState.posted,
            type=InternalMessageType.fake_message,
            source_user_technical_name=source_user_technical_name,
            target_indentifier=NodeType.master.name  # pylint: disable=no-member
        )
        message_record.send()
        return message_record

    def cron_broadcast(self, cron_command: CronWorkerCommandType, node_manager: NodeManager) -> None:
        for node in node_manager.get_record_list(node_manager.cartridge_instance.shared.bot.sudo):
            if node.type != NodeType.cron_worker:
                continue
            InternalMessage(
                message=cron_command.name,
                state=InternalMessageState.posted,
                type=InternalMessageType.cron_worker_command,
                target_indentifier=node.technical_name
            ).send()
