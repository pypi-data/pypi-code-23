import abc
from datetime import datetime, timedelta
import logging
from typing import List, Optional

from anji_orm import StringField, DatetimeField, DictField, EnumField
import rethinkdb as R

from ..types import ServicesStatus, MessageType
from ..manager import SecureModel
from ..tasks import RegularTask

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)


CONTROL_SIGNAL_ADDITIONAL_CONDITIONALS = {
    'start': lambda x: not x.is_running(),
    'stop': lambda x: x.is_running()
}


class ServiceControlTask(RegularTask):

    service_technical_name = StringField(description='Docker service technical name', definer=True)
    control_signal = StringField(description='Control signal to service', definer=True)

    def apply_signal(self, target_service: 'AbstractService') -> Optional[str]:
        control_signal = f"{self.control_signal}_signal"
        if not hasattr(target_service, control_signal):
            return None
        additional_condition = CONTROL_SIGNAL_ADDITIONAL_CONDITIONALS.get(control_signal, None)
        if additional_condition is not None and not additional_condition(target_service):
            return None
        return getattr(target_service, control_signal)() or ''

    def task_execute(self):
        target_service: 'AbstractService' = self.shared.bot.manager_env['services'].get_by_technical_name(self.service_technical_name, self.shared.bot.sudo)
        message_body = ''
        message_type = MessageType.none
        if not target_service.is_exists():
            message_body = f'Service {target_service.name} not valid'
            message_type = MessageType.error
        else:
            apply_result = self.apply_signal(target_service)
            if apply_result is not None:
                message_body = f'Signal {self.control_signal} was applied for service {target_service.name}'
                if apply_result:
                    message_body += '\n' + apply_result
                message_type = MessageType.info
            else:
                message_body = f'Signal {self.control_signal} do nothing for service {target_service.name}'
                message_type = MessageType.warning
        return dict(
            body=message_body,
            message_type=message_type,
        )

    def generate_name(self):
        return f"{self.control_signal} for service with technical name {self.service_technical_name}"


class AbstractService(SecureModel):

    hostname = StringField(description='Service server hostname', reconfigurable=True)
    access_url = StringField(description='URL link to this server', optional=True, reconfigurable=True)
    status = EnumField(ServicesStatus, default=ServicesStatus.unknown, description='Service status', displayed=False, service=True)
    status_report_time = DatetimeField(service=True, description='Service status report time')
    cartridges = DictField(service=True, displayed=False)

    display_name = 'service'

    _table = 'services'

    def apply_cartridge_configuration(self, cartridge_technical_name, cartirdge_configuration):
        # pylint guess, that cartridges are DictField, but this is field, really just a dict
        current_configuration = self.cartridges.get(cartridge_technical_name, {})  # pylint: disable=no-member
        # Cleanup cartridge configuration from None keys
        for key in list(cartirdge_configuration.keys()):
            if cartirdge_configuration.get(key) is None:
                cartirdge_configuration.pop(key)
        current_configuration.update(cartirdge_configuration)
        self.cartridges[cartridge_technical_name] = current_configuration
        self.send()

    def get_cartridge_configuration(self, cartridge_technical_name):
        if not self.is_support(cartridge_technical_name):
            self.shared.render.send(f'Unfortunately, service {self.technical_name} don\'t support command from {cartridge_technical_name} cartridge')
            return None
        return self.cartridges[cartridge_technical_name]

    def is_support(self, cartridge_technical_name):
        return self.cartridges.get(cartridge_technical_name, None)

    def get_control_task(self, control_signal):
        return ServiceControlTask(
            service_technical_name=self.technical_name,
            control_signal=control_signal
        )

    def status_healty_check(self):
        _log.info('Update status for service %s', self.technical_name)
        self.status = self.get_status()
        self.status_report_time = datetime.now(R.make_timezone("00:00"))
        self.send()

    def status_validation(self, validation_delay):
        if self.status != ServicesStatus.unknown:
            current_time = datetime.now(R.make_timezone("00:00"))
            if not self.status_report_time or (current_time - self.status_report_time) > timedelta(minutes=validation_delay):
                self.status = ServicesStatus.unknown
                self.send()

    def to_describe_dict(self, definer_skip=False):
        base_dict = super().to_describe_dict(definer_skip=definer_skip)
        if self.cartridges:
            for cartridge_name, cartridge_config in self.cartridges.items():  # pylint: disable=no-member
                cartridge = self.shared.bot.cartridge_registry.get(cartridge_name)
                if cartridge:
                    cartridge_describe = cartridge.desribe_service(cartridge_config)
                    if cartridge_describe:
                        base_dict.update(cartridge_describe)
        return base_dict

    def describe_status(self):
        if self.status in [ServicesStatus.stopped, ServicesStatus.absent]:
            return MessageType.error
        elif self.status in [ServicesStatus.restarting, ServicesStatus.unknown]:
            return MessageType.info
        return MessageType.good

    def get_status(self) -> ServicesStatus:
        self.ensure_service_registration()
        _, services_data = self.shared.consul.health.service(self.technical_name)
        if not services_data:
            return ServicesStatus.absent
        service_data = services_data[0]
        if all((lambda x: x['Status'] == 'passing' for x in service_data['Checks'])):
            return ServicesStatus.running
        return ServicesStatus.stopped

    def ensure_service_registration(self) -> None:
        _, services_data = self.shared.consul.catalog.service(self.technical_name)
        if not services_data:
            _log.info('Register service %s in consul', self.technical_name)
            self.service_registration()

    @abc.abstractmethod
    def service_registration(self) -> None:
        pass

    @abc.abstractmethod
    def fetch_unix_processes_pid(self) -> List[int]:
        pass

    @abc.abstractmethod
    def is_running(self) -> bool:
        pass

    @abc.abstractmethod
    def is_exists(self) -> bool:
        pass

    @abc.abstractmethod
    def restart_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def start_signal(self) -> bool:
        pass

    @abc.abstractmethod
    def stop_signal(self) -> bool:
        pass
