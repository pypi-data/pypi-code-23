#!/usr/bin/python3

class Processor(object):
    def __init__(self, template_set, variable_set, output_path):
        self._template_set = template_set
        self._variable_set = variable_set
        self._output_path = output_path

    def execute(self):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os.path import dirname
        from os.path import join
        from shutil import copy2
        from shutil import copystat

        for destination_name, source_path in self._template_set.constant.items():
            destination_path = join(self._output_path, destination_name)

            copy2(source_path, destination_path)

        for destination_name, source_path in self._template_set.variable.items():
            destination_path = join(self._output_path, destination_name)

            loader = FileSystemLoader(dirname(source_path))
            environment = SandboxedEnvironment(
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=False,
                autoescape=False,
                loader=loader)
            environment.globals.update(self._variable_set.data)
            template_context = {}

            with open(source_path, 'r') as source_file:
                source_text = source_file.read()

            template = environment.from_string(source_text)
            destination_text = template.render(template_context)

            with open(destination_path, 'w') as destination_file:
                destination_file.write(destination_text)

            copystat(source_path, destination_path)
