import abc

from errbot import arg_botcmd

from anji_orm import StringField, SelectionField
from anji_core.cartridges import AbstractCartridge, provide_service_configuration
from anji_core.tasks import (service_with_cartridge_interaction_task, anji_delayed_task, ServiceIteratorArgument, SimpleArgument,
                             AbstractCartridgeBashScriptTask)
from anji_core.types import Reaction
from anji_core.signals import MessageReactionSignal

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class GitAbstractTask(AbstractCartridgeBashScriptTask):

    git_operation: str = None

    @abc.abstractmethod
    def build_single_mode_command(self):
        pass

    @abc.abstractmethod
    def build_multiply_mode_command(self):
        pass

    def build_execution_command(self):
        if self.cartridge_config['type'] == 'single':
            return self.build_single_mode_command()
        return self.build_multiply_mode_command()

    def generate_short_name(self):
        return f"Git {self.git_operation} operation"

    def generate_name(self):
        return f"Git {self.git_operation} for {self.service_technical_name}"


class GitUpdateTask(GitAbstractTask):

    git_operation = 'pull'

    def build_single_mode_command(self):
        return f"git pull origin {self.cartridge_config['branch']} 2>&1"

    def build_multiply_mode_command(self):
        return f"mu pull origin {self.cartridge_config['branch']} 2>&1"


class GitFetchTask(GitAbstractTask):

    git_operation = 'fetch'

    def build_single_mode_command(self):
        return 'git fetch 2>&1'

    def build_multiply_mode_command(self):
        return 'mu fetch 2>&1'


class GitResetTask(GitAbstractTask):

    git_operation = 'reset'

    execute_command = {
        'multiply': 'mu reset {additional_keys} origin/{branch} 2>&1',
        'single': 'git reset {additional_keys} origin/{branch} 2>&1 '
    }

    card_title_template = 'Результат reset кода для сервиса {service_name}'
    card_body_template = 'Hard кода завершилось {text_result}'
    report_name_template = 'Отчет про reset кода сервиса {service_name}'

    additional_keys = StringField(description='Additional keys to git reset command', definer=True)

    def build_single_mode_command(self):
        return f"git reset {self.additional_keys} origin/{self.cartridge_config['branch']} 2>&1"

    def build_multiply_mode_command(self):
        return f"mu reset {self.additional_keys} origin/{self.cartridge_config['branch']} 2>&1"


class GitStatusTask(GitAbstractTask):

    git_operation = 'status'

    def build_single_mode_command(self):
        return 'git status 2>&1'

    def build_multiply_mode_command(self):
        return 'mu status 2>&1'


class GitCheckoutTask(GitAbstractTask):

    git_operation = 'checkout'

    def build_single_mode_command(self):
        return f"git checkout {self.cartridge_config['branch']} 2>&1"

    def build_multiply_mode_command(self):
        return f"mu checkout {self.cartridge_config['branch']} 2>&1"


@provide_service_configuration
class GitCartridge(AbstractCartridge):

    __errdoc__ = 'Git commands to control server'
    name = 'Git Commands'
    technical_name = 'base_git'
    base_command_prefix = 'git'
    service_configuration = {
        'path': StringField(description='Path to directory with repositories', reconfigurable=True),
        'branch': StringField(description='Git branch', reconfigurable=True),
        'type': SelectionField(['single', 'multiply'], description='Repository type', reconfigurable=True)
    }

    def desribe_service(self, cartridge_config):
        return {
            "Git branch": cartridge_config['branch'],
            'Git repository path': cartridge_config['path']
        }

    @service_with_cartridge_interaction_task
    def git_fetch(self, _, service_technical_name=None, service_configuration=None):
        """
        Command to fetch remote data about git repository
        """
        return GitFetchTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration
        )

    @arg_botcmd('--soft', dest='soft_reset', action='store_true', help='Disable hard reset usage')
    @service_with_cartridge_interaction_task
    def git_reset(self, _, service_technical_name=None, service_configuration=None, soft_reset=None):
        """
        Command to reset local changes in git repository.
        Default behavior: execute hard reset of local repo
        """
        git_task = GitResetTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration
        )
        if not soft_reset:
            git_task.additional_keys = '--hard'
        return git_task

    @arg_botcmd('--without-reset', dest='without_reset', action='store_true', help='Disable hard reset before code update')
    @service_with_cartridge_interaction_task
    def git_update(self, _, service_technical_name=None, service_configuration=None, without_reset=None):
        """
        Command to update local repository with remote data.
        Default behavior: hard reset local repository to ignore local changes
        """
        if not without_reset:
            return GitFetchTask(
                service_technical_name=service_technical_name,
                cartridge_config=service_configuration,
                after_task_command_list=[
                    f'git reset {service_technical_name} --delay 0',
                    f'git update {service_technical_name} --without-reset --delay 0'
                ]
            )
        return GitUpdateTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration
        )

    @service_with_cartridge_interaction_task
    def git_status(self, _, service_technical_name=None, service_configuration=None):
        """
        Command to get information about local repository status
        """
        return GitStatusTask(
            service_technical_name=service_technical_name,
            cartridge_config=service_configuration
        )

    @anji_delayed_task(
        iterators=[
            ServiceIteratorArgument(object_instead_cartridge_config=True)
        ],
        arguments=[
            SimpleArgument('new_branch', str, help='New branch name')
        ]
    )
    def git_checkout(self, mess, service_technical_name=None, service_object=None, new_branch=None):
        """
        Command to change local repository branch to another. Will update service configuration
        """
        configuration = service_object.get_cartridge_configuration(self.technical_name)
        if not configuration:
            self.shared.signals.fire(
                MessageReactionSignal(
                    mess,
                    Reaction.problem,
                    alternative_text=f"Service {service_technical_name} not configured to work with git cartridge"
                )
            )
            return None
        configuration['branch'] = new_branch
        service_object.send()
        return GitCheckoutTask(
            service_technical_name=service_technical_name,
            cartridge_config=configuration
        )
