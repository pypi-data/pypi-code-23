'''New project generator for Foliant doc buidler.'''

from pathlib import Path
from shutil import copytree
from functools import reduce
from typing import List, Dict

from cliar import Cliar, set_help, set_arg_map, set_metavars
from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

from slugify import slugify

from foliant.utils import spinner


class BuiltinTemplateValidator(Validator):
    '''Validator for the interactive template selection prompt.'''

    def __init__(self, builtin_templates: List[str]):
        super().__init__()
        self.builtin_templates = builtin_templates

    def validate(self, document):
        '''Check if the selected template exists.'''

        template = document.text

        if template not in self.builtin_templates:
            raise ValidationError(
                message=f'Template {template} not found. '
                + f'Available templates are: {", ".join(self.builtin_templates)}.',
                cursor_position=0
            )


def replace_placeholders(path: Path, values: Dict[str, str]):
    '''Replace placeholders in a file with the values from the mapping.'''

    with open(path, encoding='utf8') as file:
        file_content = file.read()

    with open(path, 'w', encoding='utf8') as file:
        file.write(file_content.format_map(values))


class Cli(Cliar):
    @set_arg_map({'project_name': 'name'})
    @set_metavars({'project_name': 'NAME', 'template': 'NAME or PATH'})
    @set_help(
        {
            'project_name': 'Name of the Foliant project',
            'template': 'Name of a built-in project template or path to custom one',
            'quiet': 'Hide all output accept for the result. Useful for piping.'
        }
    )
    def init(self, project_name='', template='basic', quiet=False):
        '''Generate new Foliant project.'''

        template_path = Path(template)

        if not template_path.exists():
            builtin_templates_path = Path(__file__).parent / 'templates'

            builtin_templates = [
                item.name for item in builtin_templates_path.iterdir() if item.is_dir()
            ]

            if template not in builtin_templates:
                try:
                    template = prompt(
                        f'Please pick a template from {builtin_templates}: ',
                        completer=WordCompleter(builtin_templates),
                        validator=BuiltinTemplateValidator(builtin_templates)
                    )

                except KeyboardInterrupt:
                    return

            template_path = builtin_templates_path / template

        if not project_name:
            project_name = prompt('Enter the project name: ')

        project_slug = slugify(project_name)

        project_path = Path(project_slug)

        values = {
            'title': project_name,
            'slug': project_slug
        }

        result = None

        with spinner('Generating Foliant project', quiet):
            copytree(template_path, project_path)

            text_types = '*.md', '*.yml', '*.txt'

            text_file_paths = reduce(
                lambda acc, matches: acc + [*matches],
                (project_path.rglob(text_type) for text_type in text_types),
                []
            )

            for text_file_path in text_file_paths:
                replace_placeholders(text_file_path, values)

            result = project_path

        if result:
            if not quiet:
                print('─────────────────────')
                print(f'Project "{project_name}" created in {result}')
            else:
                print(result)

        else:
            exit(1)
