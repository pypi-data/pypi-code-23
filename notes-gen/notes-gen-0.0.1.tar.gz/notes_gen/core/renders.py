import os
import shutil

from slugify import slugify
from jinja2 import Template

from notes_gen.core.utils import Pandoc
from notes_gen.core.exceptions import PandocException, ImproperlyConfiguredException


class BaseRender:

    def execute(self, site):
        '''Subclass must implement this method. It will be called during the rendering process.
        '''
        raise NotImplementedError('Subclass of BaseRender must implement execute method')


class PandocRender:

    _INDEX_LAYOUT = 'index.html'
    _NOTES_LAYOUT = 'notes.html'

    _error_message = {
        'pandoc_error': 'Cant run pandoc. Check if pandoc is install with latex support.',
        'file_missing': 'Improperly configured. Missing file "{path}"'
    }

    def _generate_html_from_layout(self, public_notes_path, file_obj, site):
        '''Render notes from layout template
        '''
        # Conver markdown to html string
        html_content = Pandoc.to_html_string(public_notes_path)

        # Html file path
        html_file_path = os.path.join(os.path.dirname(public_notes_path), slugify(file_obj['meta']['title']) + '.html')

        # Get notes_layout
        note_layout_file = os.path.join(site['folders']['layout'], self._NOTES_LAYOUT)
        if os.path.isfile(note_layout_file) is False:
            msg = self._error_message['file_missing'].format(path=note_layout_file)
            raise ImproperlyConfiguredException(msg)

        # Read layout
        with open(note_layout_file, 'r') as file:
            tempate = Template(file.read())

        # render layout using jinga
        template_context = {
            'title': file_obj['meta']['title'],
            'category': file_obj['meta']['category'],
            'description': file_obj['meta']['description'],
            'content': html_content,
        }

        # Render html
        with open(html_file_path, 'w') as file:
            file.write(tempate.render(note=template_context))

        # Add path to file object
        file_obj['html_path'] = html_file_path

    def _render_index_page(self, site):

        # Get index file path
        index_file_path = os.path.join(site['projects_folder'], 'index.html')

        # Get index_layout
        index_layout_file = os.path.join(site['folders']['layout'], self._INDEX_LAYOUT)
        if os.path.isfile(index_layout_file) is False:
            msg = self._error_message['file_missing'].format(path=index_layout_file)
            raise ImproperlyConfiguredException(msg)

        # Read layout
        with open(index_layout_file, 'r') as file:
            tempate = Template(file.read())

        # Template context
        tempate_context = []
        categories = set()
        _optional_template_key = ['pdf_path', 'latex_path', 'html_path', 'markdown_path']
        project_folder_path = site['projects_folder']
        for file_obj in site['markdown_files']:
            note_object = {
                'title': file_obj['meta']['title'],
                'category': file_obj['meta']['category'],
                'description': file_obj['meta']['description'],

            }

            # Add optional keys
            for key in _optional_template_key:
                if key in file_obj:
                    note_object[key] = file_obj[key].replace(project_folder_path, '')

            tempate_context.append(note_object)
            [categories.add(cat) for cat in file_obj['meta']['category']]

        # Write index.html page
        with open(index_file_path, 'w') as file:
            file.write(tempate.render(notes=tempate_context, categories=list(categories)))

    def execute(self, site):
        '''A wrapper around pandoc
        '''

        public_folder = site['folders']['public']

        is_pdf = site['generate_pdf']
        is_html = site['generate_html']
        is_latex = site['generate_latex']
        is_root_index = site['root_index_page']

        # Render each notes
        for file_obj in site['markdown_files']:

            # Generate public notes path
            notes_path = file_obj['path']
            notes_path = notes_path.replace(site['folders']['notes'], '')
            if notes_path.startswith('/'):
                notes_path = notes_path[1:]
            public_notes_path = os.path.join(public_folder, os.path.dirname(notes_path))
            public_notes_path = os.path.join(public_notes_path, slugify(file_obj['meta']['title'].replace('.md', '')) + '.md')

            # Create directory
            os.makedirs(os.path.dirname(public_notes_path), exist_ok=True)

            # Copy markdown file to the folder
            shutil.copyfile(file_obj['path'], public_notes_path)
            file_obj['markdown_path'] = public_notes_path

            # Copy assets folder
            assets_folder = file_obj.get('assets', None)
            if assets_folder is not None:
                public_assets_folder = os.path.join(public_folder, os.path.dirname(notes_path))
                public_assets_folder = os.path.join(public_assets_folder, os.path.basename(assets_folder))
                if os.path.exists(public_assets_folder) is False:
                    shutil.copytree(assets_folder, public_assets_folder)

            # Convert markown to pdf
            if is_pdf is True:
                pdf_file_path = os.path.join(os.path.dirname(public_notes_path), slugify(file_obj['meta']['title']) + '.pdf')
                try:
                    Pandoc.file_to_pdf(public_notes_path, pdf_file_path)
                except PandocException:
                    raise PandocException(self._error_message['pandoc_error'])
                finally:
                    file_obj['pdf_path'] = pdf_file_path

            # Convert markdown to latex
            if is_latex is True:
                latex_file_path = os.path.join(os.path.dirname(public_notes_path), slugify(file_obj['meta']['title']) + '.latex')
                try:
                    Pandoc.file_to_latex(public_notes_path, latex_file_path)
                except PandocException:
                    raise PandocException(self._error_message['pandoc_error'])
                finally:
                    file_obj['latex_path'] = latex_file_path

            # Convert markdown to html
            if is_html is True:
                self._generate_html_from_layout(public_notes_path, file_obj, site)

        # Render the index page
        if is_html is True and is_root_index is True:
            self._render_index_page(site)
