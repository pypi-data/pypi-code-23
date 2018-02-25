import os
import re
import json
import glob


from notes_gen.core.exceptions import MarkdownException


class ProjectReader:
    '''Class which create a site data structure to desrcibe the components of the site
    '''

    _REGEX_PREAMBLE = r"---(?P<content>\n[\s\S]*?\n)*---"

    _error_message = {
        'invalid_meta': 'Invalid meta for markdown file {path}.'
    }

    _ASSESTS_FOLDER = 'assets'

    @classmethod
    def create(cls, settings):
        '''Create a site dict which contains projects information
        '''
        site = settings.copy()

        cls.__add_markdown_files(site)

        # Add a list for clearner
        site['cleanup'] = []

        return site

    @classmethod
    def __add_markdown_files(cls, site):
        '''Read _notes folder and create a list of markdown files objects
        '''

        markdown_files = []

        notes_folder = os.path.join(site['projects_folder'], site['folders']['notes'])

        markdown_pattern = '{}/**/*.md'.format(notes_folder)
        for file_path in glob.iglob(markdown_pattern, recursive=True):

            markdown_object = {
                'path': file_path
            }

            # Add assets folder
            assets_folder = os.path.join(os.path.dirname(file_path), cls._ASSESTS_FOLDER)
            if os.path.exists(assets_folder) is True:
                markdown_object.update({
                    'assets': assets_folder
                })

            # Read markdown
            with open(file_path, 'r') as file:
                content = file.read()

            # Get preamble from markdown
            preamble = re.search(cls._REGEX_PREAMBLE, content)
            if preamble is not None:
                try:
                    markdown_object['meta'] = json.loads(preamble.group('content'))
                except json.JSONDecodeError:
                    msg = cls._error_message['invalid_meta'].format(path=file_path)
                    raise MarkdownException(msg)
            else:
                markdown_object['meta'] = {}

            markdown_files.append(markdown_object)

        # Add markdown files to site
        site['markdown_files'] = markdown_files
