#!python

from argparse import ArgumentParser

arg_parser = ArgumentParser(description='.')
arg_parser.add_argument(
    '--templates', '-t',
    required=True,
    dest='template_paths',
    action='append',
    metavar='path/to/teplates',
    help='Path to directory with template files')
arg_parser.add_argument(
    '--variables', '-v',
    required=True,
    dest='variable_paths',
    action='append',
    metavar='path/to/variables',
    help='Path to directory with variable files')
arg_parser.add_argument(
    '--output', '-o',
    required=True,
    dest='output_path',
    action='store',
    metavar='path/to/output',
    help='Path to directory with output')

args = arg_parser.parse_args()

from variable import VariableSet

variable_set = VariableSet()

for variable_path in args.variable_paths:
    variable_set.add_path(variable_path)

from template import TemplateSet

template_set = TemplateSet()

for template_path in args.template_paths:
    template_set.add_path(template_path)

from processor import Processor

processor = Processor(template_set, variable_set, args.output_path)
processor.execute()
