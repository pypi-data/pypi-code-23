from errbot import arg_botcmd
from sarge import Capture, run

from anji_orm import StringField, SelectionField, BooleanField
from anji_core.cartridges import AbstractCartridge, provide_service_configuration
from anji_core.tasks import AbstractCartridgeBashScriptTask, anji_delayed_task, ServiceIteratorArgument, ServiceTaskSignalProducer, service_with_cartridge_interaction_task
from anji_core.types import ServiceUnavailableType, Reaction
from anji_core.signals import MessageReactionSignal

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.2"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class OdooOperateModelesTask(AbstractCartridgeBashScriptTask):

    _path_field = 'makefile_directory'

    modules = StringField(description='Modules list', definer=True)
    target_action = SelectionField(['install', 'update'], description='Action for modules', definer=True)
    test_mode = BooleanField(description='Execute this task for test modules', definer=True)

    def generate_short_name(self):
        return f'Modules {self.target_action} for {"test" if self.test_mode else "real"} databases'

    def build_execution_command(self):
        return f'make {"test" if self.test_mode else "simple"}-{self.target_action} modules="{self.modules}" 2>&1'

    def generate_name(self):
        return f'Modules {self.target_action} for {"test" if self.test_mode else "real"} databases for {self.service_technical_name}'


class OdooRunTestTask(AbstractCartridgeBashScriptTask):

    _path_field = 'makefile_directory'

    def generate_short_name(self):
        return 'Test run'

    def build_execution_command(self):
        return 'make test 2>&1'

    def task_execute(self):
        result_dict = super().task_execute()
        curl_process = run(
            'make test-report',
            stdout=Capture(),
            cwd=self.cartridge_config['makefile_directory']
        )
        pytest_html_report_link = self.shared.report.transform_url(curl_process.stdout.readlines()[-1].decode('UTF-8'))
        result_dict['reports'].append(('HTML test report run', pytest_html_report_link))
        return result_dict

    def generate_name(self):
        return f"Test run for service {self.service_technical_name}"


@provide_service_configuration
class OdooCartridge(AbstractCartridge):

    __errdoc__ = 'Odoo commands to control server'
    name = 'Odoo Commands'
    technical_name = 'base_odoo'
    base_command_prefix = 'odoo'
    service_configuration = {
        'makefile_directory': StringField(description='Path to makefile directory', reconfigurable=True),
    }

    @arg_botcmd('--test', dest='test_flag', action='store_true', help='Run update for databases that used in tests')
    @arg_botcmd('--modules', dest='modules', help='Modules list (only comma, no spaces)')
    @arg_botcmd('--all', dest='all_modules', action='store_true', help='Run for all modules')
    @anji_delayed_task(
        iterators=[
            ServiceIteratorArgument()
        ],
        producers=[
            ServiceTaskSignalProducer(ServiceUnavailableType.taskwide)
        ]
    )
    def odoo_update_modules(self, mess, service_technical_name=None, service_configuration=None, test_flag=None, modules=None, all_modules=None):
        """
        Command to execute odoo modules update on target service
        """
        if not modules and not all_modules:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.empty,
                    alternative_text='Can you please define, what I must to update?'
                )
            )
            return None
        return OdooOperateModelesTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration,
            modules=modules if not all_modules else "all",
            test_mode=test_flag,
            target_action='update'
        )

    @arg_botcmd('--test', dest='test_flag', action='store_true', help='Run update for databases that used in tests')
    @arg_botcmd('--modules', dest='modules', help='Modules list (only comma, no spaces)')
    @anji_delayed_task(
        iterators=[
            ServiceIteratorArgument()
        ],
        producers=[
            ServiceTaskSignalProducer(ServiceUnavailableType.taskwide)
        ]
    )
    def odoo_install_modules(self, mess, service_technical_name=None, service_configuration=None, test_flag=None, modules=None):
        """
        Command to execute odoo modules install on target service
        """
        if not modules:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.empty,
                    alternative_text='Can you please define, what I must to install?'
                )
            )
            return None
        return OdooOperateModelesTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration,
            modules=modules,
            test_mode=test_flag,
            target_action='install'
        )

    @service_with_cartridge_interaction_task
    def odoo_test(self, _, service_technical_name=None, service_configuration=None):
        """
        Command to run odoo test with pytest help
        """
        return OdooRunTestTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration,
        )
