from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'macros': {}
    }
    tags = 'macro', 'm'

    def process_macros(self, content: str) -> str:
        '''Replace macros with content defined in the config.

        :param content: Markdown content

        :returns: Markdown content without macros
        '''

        def _sub(macro):
            name = macro.group('body')
            params = self.get_options(macro.group('options'))

            return self.options['macros'].get(name, '').format_map(params)

        return self.pattern.sub(_sub, content)

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.process_macros(content))
