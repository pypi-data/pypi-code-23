import logging

from errbot import botcmd

from ..cartridges import AbstractCartridge, provide_confirmation_logic
from .core import AbstractService
from ..types import ServiceUnavailableType
from ..security import guard
from ..tasks import anji_delayed_task, ServiceIteratorArgument, ServiceTaskSignalProducer, service_interaction_task
from ..manager import SecurityManager

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)


@provide_confirmation_logic
class ServicesCartridge(AbstractCartridge):

    __errdoc__ = 'Core commands to control services'
    name = 'Core services commands'
    technical_name = 'core_services'
    base_command_prefix = 'service'

    @guard.admin_only_command
    @botcmd(split_args_with=None)
    def service_refresh(self, _mess, _args):
        """
        Service list update
        """
        self.manager.update_service_list()

    @anji_delayed_task(
        iterators=[
            ServiceIteratorArgument(object_instead_cartridge_config=True)
        ],
        producers=[
            ServiceTaskSignalProducer(ServiceUnavailableType.temporary)
        ]
    )
    def service_restart(self, _, service_technical_name=None, service_object=None):
        """
        Command to service restart
        """
        return self.manager.control_service(service_technical_name, service_object, 'restart')

    @service_interaction_task
    def service_stop(self, _, service_technical_name=None, service_object=None):
        """
        Command to service stop
        """
        return self.manager.control_service(service_technical_name, service_object, 'stop')

    @service_interaction_task
    def service_start(self, _, service_technical_name=None, service_object=None):
        """
        Command to service start
        """
        return self.manager.control_service(service_technical_name, service_object, 'start')

    @service_interaction_task
    def service_update(self, _, service_technical_name=None, service_object=None):
        """
        Command to service recreate or creation if it was destroyed
        """
        return self.manager.control_service(service_technical_name, service_object, 'update')

    @service_interaction_task
    def service_destroy(self, _, service_technical_name=None, service_object=None):
        """
        Command to service descroy
        """
        return self.manager.control_service(service_technical_name, service_object, 'destroy')


class ServicesManager(SecurityManager):

    controlled_model = AbstractService
    controlled_cartridge = ServicesCartridge
    submodel_use_model_table = True
    control_prefix = 'service'

    @property
    def manager_short_name(self) -> str:
        return "services"

    def __init__(self, bot):
        super().__init__(bot)
        self.service_validation_delay = None

    def load(self):
        self.service_validation_delay = self.bot.configuration['core']['service_validation_delay']
        super().load()

    def update_record_list(self, with_push=False):
        super().update_record_list(with_push=with_push)
        for model in self._models.values():
            model.status_validation(self.service_validation_delay)

    def global_healthy_check(self, force_registration=False) -> None:
        _log.info('Cause global healthy check')
        for service in self.get_record_list(self.bot.sudo):
            if service.hostname == self.bot.node.hostname:
                if force_registration:
                    service.service_registration()
                service.status_healty_check()

    def is_external(self, service_technical_name):
        service = self._models.get(service_technical_name)
        if service:
            return service.hostname == self.bot.bot_config.ANJI_HOSTNAME
        return False

    def control_service(self, _1, service_object, control_signal):  # pylint: disable=no-self-use
        return service_object.get_control_task(control_signal)

    def get_all_service_names(self):
        return self._models.keys()
