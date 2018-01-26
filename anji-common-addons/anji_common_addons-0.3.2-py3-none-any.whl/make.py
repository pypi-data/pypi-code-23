from anji_orm import StringField
from anji_core.cartridges import AbstractCartridge, provide_service_configuration
from anji_core.tasks import AbstractCartridgeBashScriptTask, anji_delayed_task, ServiceIteratorArgument, SimpleArgument

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class MakefileTask(AbstractCartridgeBashScriptTask):

    make_command = StringField(description='Make command to execute', definer=True)

    _path_field = 'makefile_directory'

    def build_execution_command(self):
        return f'make {self.make_command} 2>&1'

    def generate_short_name(self):
        return f'Make command {self.make_command}'

    def generate_name(self):
        return f"Make command {self.make_command} execution for service {self.service_technical_name}"


@provide_service_configuration
class MakeCartridge(AbstractCartridge):

    __errdoc__ = 'Makefile commands to control server'
    name = 'Make Commands'
    technical_name = 'makefile'
    base_command_prefix = 'make'
    service_configuration = {
        'makefile_directory': StringField(description='Path to makefile directory', reconfigurable=True),
    }

    @anji_delayed_task(
        iterators=[
            ServiceIteratorArgument()
        ],
        arguments=[
            SimpleArgument('make_command', str, help='Command to execute with make')
        ]
    )
    def make(self, _, make_command=None, service_technical_name=None, service_configuration=None):
        """
        Command just to execution make command on service
        """
        return MakefileTask(
            make_command=make_command,
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration
        )
