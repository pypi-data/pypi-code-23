import os
import sys
import shutil
from slugify import slugify

import notes_gen
from notes_gen.core.managment.base import BaseCommand
from notes_gen.core.settings import ProjectSettings
from notes_gen.core.projectreader import ProjectReader
from notes_gen.core.loggers import ConsoleLogger
from notes_gen.core.exceptions import ImproperlyConfiguredException, MarkdownException

logger = ConsoleLogger()


class Command(BaseCommand):
    '''Command to create new notes
    '''

    description = 'Start new notes'

    _error_message = {
        'folder_exists': '"{path}" folder already exists.',
        'cant_create_project': 'Couldnt create a project at path "{path}"',
    }

    _ASSESTS_FOLDER = 'assets'
    _FILE_TEMPLATE = '''
---
{
    "main": true,
    "title": "%(title)s",
    "description": "%(description)s",
    "category": [%(category)s]
}

---
'''

    def add_arguments(self, parser):
        '''Add Command line arguments
        '''
        pass

    def execute(self, arguements):
        '''Create new folder logger with project_name and copy the template dir
        '''
        try:
            settings = ProjectSettings.read(os.getcwd())
        except ImproperlyConfiguredException as e:
            logger.error(e)
            sys.exit()

        try:
            site = ProjectReader.create(settings)
        except MarkdownException as e:
            logger.error(e)
            sys.exit()

        note_name = input('What name do u want for your note: ')
        slug_nots_name = slugify(note_name)

        note_description = input('Give a small description of the note: ')

        note_category = input('Give a comma seprated category: ')
        note_category = note_category.split(',')

        file_path = input('Folder for notes[{}.md]: '.format(slug_nots_name))
        if len(file_path) == 0:
            file_path = '{}.md'.format(slug_nots_name)
        file_path = os.path.join(site['folders']['notes'], file_path)

        # Make dirs
        try:
            os.makedirs(os.path.dirname(file_path))
        except Exception:
            pass

        # Create assets folder
        try:
            os.mkdir(os.path.join(os.path.dirname(file_path), self._ASSESTS_FOLDER))
        except Exception:
            pass

        # Create File
        with open(file_path, 'w') as file:
            data = {
                'title': note_name,
                'description': note_description,
                'category': ','.join([
                    '"{}"'.format(item) for item in note_category
                ])
            }
            content = self._FILE_TEMPLATE % data
            file.write(content)

        logger.success('Done!!')
