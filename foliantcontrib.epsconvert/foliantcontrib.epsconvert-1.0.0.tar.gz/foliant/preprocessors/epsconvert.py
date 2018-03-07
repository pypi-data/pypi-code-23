'''
Preprocessor for Foliant documentation authoring tool.
Converts EPS images to PNG format.
'''

import re

from pathlib import Path
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'mogrify_path': 'mogrify',
        'image_width': 0
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pattern = re.compile(
            r"!\[(?P<caption>.+)\]\((?P<path>.+)\.eps\)"
        )

    def process_eps_paths(self, content: str) -> str:

        fixed_content = re.sub(
            self.pattern,
            r"![\g<caption>](\g<path>.png)",
            content
        )

        return fixed_content

    def apply(self):
        if self.context["target"] != 'pdf':
            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(self.process_eps_paths(content))

            mogrify_geometry = ''

            if self.options["image_width"] > 0:
                mogrify_geometry = f'-geometry {self.options["image_width"]}'

            for eps_file_path in self.working_dir.rglob('*.eps'):
                try:
                    command = f'{self.options["mogrify_path"]} -format png {mogrify_geometry} {eps_file_path}'
                    run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                except CalledProcessError as exception:
                    raise RuntimeError(f'Failed: {exception.output.decode()}')

                try:
                    Path(eps_file_path).unlink()

                except PermissionError:
                    pass
