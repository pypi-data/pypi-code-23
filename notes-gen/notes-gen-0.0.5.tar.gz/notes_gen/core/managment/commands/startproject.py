import os
import sys
import shutil

import notes_gen
from notes_gen.core.managment.base import BaseCommand
from notes_gen.core.loggers import ConsoleLogger

logger = ConsoleLogger()


class Command(BaseCommand):
    '''Command to create a starter project template.
    '''

    description = 'Create new project with a given project_name'

    _TEMPLATE_DIR = 'template'

    _error_message = {
        'folder_exists': '"{path}" folder already exists.',
        'cant_create_project': 'Couldnt create a project at path "{path}"',
    }

    def add_arguments(self, parser):
        '''Add Command line arguments
        '''
        parser.add_argument('project_name', help='Name of the project.')

    def execute(self, arguements):
        '''Create new folder logger with project_name and copy the template dir
        '''
        project_dir = os.path.join(os.getcwd(), arguements.project_name)

        # Check if folder already exists
        if os.path.exists(project_dir) is True:
            logger.error(self._error_message['folder_exists'].format(path=project_dir))
            sys.exit()

        # Copy tempates dir to project path
        template_dir = os.path.join(os.path.dirname(notes_gen.__file__), self._TEMPLATE_DIR)
        try:
            shutil.copytree(template_dir, project_dir)
        except OSError:
            # Error
            logger.error(self._error_message['cant_create_project'].format(path=project_dir))
            sys.exit()
        else:
            # Success
            logger.success('Created a project at "{path}".'.format(path=project_dir))
