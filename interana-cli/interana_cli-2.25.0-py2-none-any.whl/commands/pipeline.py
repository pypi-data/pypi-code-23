# Copyright 2017 Interana, Inc.
'''
ia pipeline create test_pipeline test_table aws
ia pipeline list
ia pipeline show
ia pipeline delete
'''

import ast
import json
import os
from collections import OrderedDict

from ..utils import samples
from ..utils.command_utils import DATA_SOURCE_TYPES, PIPELINE_LIST_COLUMNS, print_example_config
from ..utils.completers import DataSourceTypeCompleter, PipelineParameterCompleter, PipelinesCompleter, TablesCompleter
from ..utils.shared_parsers import add_example_config, add_output_parameters, add_run_mode


from base import CommandHandler, DoResult, SubCommandHandler


class PipelineHandler(CommandHandler):

    name = 'pipeline'
    description = 'Commands for managing ingest pipelines.'

    def __init__(self):
        CommandHandler.__init__(self)
        self.register_subcommands(PipelineCreate(),
                                  PipelineClone(),
                                  PipelineList(),
                                  PipelineShow(),
                                  PipelineDelete(),
                                  PipelineExport(),
                                  PipelineUpdate())


class PipelineCreate(SubCommandHandler):

    name = 'create'
    description = ('Create a new pipeline by specifying the pipeline name, table name, data source type, and '
                   'connection parameters, or through a configuration file.')

    example_commands = [
        ('Example', 'ia pipeline create my_pipeline my_table aws -p s3_bucket my_bucket -p file_pattern '
                    '"{year}/{month:02d}/{day:02d}/{hour:02d}/logs" -p concat_file_size 1000000000 '
                    '--transformation-config my_transformer_config.txt')
    ]

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        add_example_config(parser)
        parser.add_argument(
            'pipeline_name',
            help='Name of pipeline to create.',
            type=str,
            nargs='?'
        )
        parser.add_argument(
            'table_name',
            help='Name of the table the pipeline should import data to.',
            type=str,
            nargs='?'
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'data_source_type',
            help=('Type of data source pipeline will be ingesting data from. Choices include: {}.'
                  .format(', '.join(DATA_SOURCE_TYPES))),
            type=str,
            nargs='?'
        ).completer = DataSourceTypeCompleter(self)
        parser.add_argument(
            '-t',
            '--transformation-config',
            help='Path to file with transformation configuration.',
            type=str,
        )
        parser.add_argument(
            '-p',
            '--parameter',
            help='Parameter and value to add to pipeline configuration.',
            type=str,
            nargs=2,
            metavar=('PARAMETER NAME', 'VALUE'),
            action='append'
        ).completer = PipelineParameterCompleter(self, query_parameter='data_source_type')
        parser.add_argument(
            '--config-file',
            help='Path to the dataset configuration file.',
            type=str
        )

        return parser

    def do(self):
        if self.args.example_config:
            print_example_config('Pipeline Create', samples.PIPELINE_CREATE_SAMPLE)
            return

        pipeline_create_args = [self.args.pipeline_name, self.args.table_name, self.args.data_source_type]
        if not any(pipeline_create_args) and not self.args.config_file:
            raise Exception('Either pipeline creation parameters or a configuration file must be specified.')

        if any(pipeline_create_args) and self.args.config_file:
            raise Exception('Both pipeline creation parameters and a configuration file may not be specified. Please '
                            'specify only one option.')

        if any(pipeline_create_args) and not all(pipeline_create_args):
            raise Exception('When specifying pipeline creation parameters, pipeline_name, table_name, '
                            'and data_source_type must all be specified.')

        if self.args.transformation_config and self.args.config_file:
            raise Exception('When using a config file, transformation configurations must be part of the '
                            'config file.')

        pipeline_config = None
        if self.args.config_file:
            if not os.path.isfile(self.args.config_file):
                raise Exception('"{}" is not a file'.format(self.args.config_file))
            with open(self.args.config_file, 'rb') as config_fh:
                config_text = config_fh.read()
                try:
                    pipeline_config = ast.literal_eval(config_text)
                except:
                    try:
                        pipeline_config = json.loads(config_text)
                    except:
                        raise Exception('Could not load pipeline configuration from file: "{}"'
                                        .format(self.args.config_file))
        else:
            # command line args
            if not self.args.parameter:
                raise Exception('Pipeline parameters (using -p/--parameter) must be provided')

            pipeline_dict = {
                'name': self.args.pipeline_name,
                'data_source_type': self.args.data_source_type,
                'table_name': self.args.table_name,
                'data_source_parameters': {param[0]: param[1] for param in self.args.parameter}
            }

            if self.args.transformation_config:
                if not os.path.isfile(self.args.transformation_config):
                    raise Exception('"{}" is not a file'.format(self.args.transformation_config))

                with open(self.args.transformation_config, 'rb') as config_fh:
                    try:
                        transformation_config = config_fh.read()
                        ast.literal_eval(transformation_config)
                    except:
                        raise Exception('could not load transformation configuration from file "{}".'
                                        .format(self.args.transformation_config))

                pipeline_dict['data_transformations'] = transformation_config
            pipeline_config = {'ingest': [pipeline_dict]}

        res = self.post_json('{hostname}/import/api/ingest/pipeline/create', data=pipeline_config)
        content = json.loads(res.content)

        entries = [[f[0](r) for f in PIPELINE_LIST_COLUMNS] for r in content.values()]
        msg = ''
        if entries:
            msg = 'Successfully created pipeline(s): {}'.format(','.join([r for r in content]))

        return DoResult(entries=entries, headers=[tc[1] for tc in PIPELINE_LIST_COLUMNS], message=msg)


class PipelineClone(SubCommandHandler):

    name = 'clone'
    description = 'Clone an existing ingest pipeline. Can override original pipeline\'s parameters.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'pipeline_name',
            help='Name of existing pipeline to clone.',
            type=str
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            'pipeline_clone_name',
            help='Name of new, cloned pipeline.',
            type=str
        )
        parser.add_argument(
            '-p',
            '--parameter',
            help='Parameter and value that override original pipeline\'s parameters for new pipeline.',
            type=str,
            nargs=2,
            metavar=('PARAMETER NAME', 'VALUE'),
            action='append',
            default=[]
        ).completer = PipelineParameterCompleter(self, query_parameter='pipeline_name')

        return parser

    def do(self):
        pipeline_dict = {
          'pipeline_name': self.args.pipeline_name,
          'pipeline_clone_name': self.args.pipeline_clone_name,
          'data_source_parameters': {param[0]: param[1] for param in self.args.parameter},
        }

        res = self.post_json('{hostname}/import/api/ingest/pipeline/clone', data=pipeline_dict)
        content = json.loads(res.content)

        entries = [[f[0](content) for f in PIPELINE_LIST_COLUMNS]]
        msg = ''
        if entries:
            msg = 'Successfully cloned pipeline "{}" to pipeline "{}"'\
                  .format(self.args.pipeline_name, self.args.pipeline_clone_name)

        return DoResult(entries=entries, headers=[tc[1] for tc in PIPELINE_LIST_COLUMNS], message=msg)


class PipelineList(SubCommandHandler):

    name = 'list'
    description = 'List ingest pipelines. Can filter based on table.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            '-t',
            '--table',
            help='List pipelines for the given table.',
            type=str,
        ).completer = TablesCompleter(self)

        return parser

    def do(self):
        params = {
            'table': self.args.table,
        }
        res = self.post_json('{hostname}/import/api/ingest/list_pipelines', data=params)
        content = json.loads(res.content)

        entries = [[f[0](r) for f in PIPELINE_LIST_COLUMNS] for r in content.get('pipelines', [])]

        table_msg = " for table '{}'".format(self.args.table) if self.args.table else ""
        empty_warning = "No pipelines{} were found.".format(table_msg)

        return DoResult(entries=entries, headers=[tc[1] for tc in PIPELINE_LIST_COLUMNS], empty_warning=empty_warning)


class PipelineShow(SubCommandHandler):

    name = 'show'
    description = 'Display the details of a pipeline.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'pipeline_name',
            help='Name of pipeline to show details.',
            type=str,
        ).completer = PipelinesCompleter(self)

        return parser

    def do(self):
        params = {
            'pipeline_name': self.args.pipeline_name,
        }
        res = self.post_json('{hostname}/import/api/ingest/show_pipeline', data=params)
        pipeline = json.loads(res.content)
        entries = [
            ['ID', pipeline['pipeline_id']],
            ['Name', pipeline['name']],
            ['Table', pipeline['table_name']],
            ['Data Source', pipeline['data_source_type']],
            ['Description', pipeline['description']],
            ['Data Source Parameters', pipeline['data_source_parameters']],
            ['Advanced Parameters', pipeline.get('advanced_parameters', {})],
            ['Transformations', pipeline['data_transformations']],
        ]

        empty_warning = "No pipelines with name '{}' were found".format(self.args.pipeline_name)

        return DoResult(entries=entries, headers=['Key', 'Value'], empty_warning=empty_warning)


class PipelineDelete(SubCommandHandler):

    name = 'delete'
    description = ('Delete the named pipelines or delete pipelines associated with specified table.'
                   'Defaults to dry-run mode.')

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'pipeline_name',
            help='Name of pipeline to be deleted.',
            type=str,
            nargs='*'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-t',
            '--table',
            help='Delete pipelines for the given table.',
            type=str,
        ).completer = TablesCompleter(self)
        add_run_mode(parser)

        return parser

    def do(self):
        pipeline_names = self.args.pipeline_name
        table_name = self.args.table
        params = {
            'pipeline_names': pipeline_names,
            'dry_run': 1 if self.args.run is 0 else 0,  # api takes in dry_run, which is opposite of run
            'table_name': table_name
        }
        if not pipeline_names and not table_name:
            raise Exception('A table name or pipelines need to be specified')

        if pipeline_names and table_name:
            raise Exception('Either a table name or pipelines need to be specified, not both.')
        entries = []
        print 'Initiating deletion {}for {}, please wait...\n'.format(
              'preview ' if not self.args.run else '',
              'pipelines of table ' + table_name if table_name else 'pipelines ' + ', '.join(pipeline_names))

        res = self.post_json('{hostname}/import/api/pipeline/delete', data=params)
        content = json.loads(res.content)
        if content:
            entries = [[pipeline] for pipeline in content.get('pipelines', [])]

        empty_warning = "No pipelines with name '{}' were found".format(pipeline_names)
        headers = ['Deleted Pipeline'] if self.args.run else ['Preview Delete Pipeline']

        next_action = ''
        if not self.args.run:
            next_action = ('This is a preview mode. Rerun with --run option to delete pipeline(s) {}.'
                           .format(', '.join(self.args.pipeline_name)))

        return DoResult(entries=entries, headers=headers, empty_warning=empty_warning, message=next_action)


class PipelineExport(SubCommandHandler):

    name = 'export'
    description = 'Export ingest pipeline configurations to a file.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        parser.add_argument(
            'pipeline_name',
            help='Name of ingest pipelines to export. Can specify multiple pipelines.',
            type=str,
            nargs='+'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-o',
            '--output-file',
            help='File to write configuration to. Default output file is '
            '<ingest pipeline name>_pipeline_config.txt in the current directory.',
            type=str
        )
        return parser

    def do(self):
        output_file = '{}_pipeline_config.txt'.format('_'.join(self.args.pipeline_name))
        if self.args.output_file:
            output_file = self.args.output_file
            if os.path.isfile(output_file):
                print 'Note: a file exists at \'{}\', it will be overwritten.'.format(output_file)
        else:
            print 'No output-file specified, exporting to file \'{}\''.format(output_file)

        params = {
            'pipeline_names': self.args.pipeline_name,
        }
        res = self.post_json('{hostname}/import/api/ingest/pipeline/export', data=params)
        content = json.loads(res.content, object_pairs_hook=OrderedDict)
        try:
            with open(output_file, 'w') as out_fh:
                out_fh.write(json.dumps(content, indent=4))
        except:
            print 'Error writing to file: {}'.format(output_file)
            raise


class PipelineUpdate(SubCommandHandler):

    name = 'update'
    description = ('Update an existing pipeline\'s parameters and transformation config or '
                   'update multiple pipelines through a configuration file.')

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        add_example_config(parser)
        parser.add_argument(
            'pipeline_name',
            help='Name of pipeline to update.',
            type=str,
            nargs='?'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-p',
            '--parameter',
            help='Name of parameter and value to update to. '
            'Can be specified multiple times to update multiple parameters.',
            nargs=2,
            metavar=('PARAMETER NAME', 'VALUE'),
            action='append'
        ).completer = PipelineParameterCompleter(self, query_parameter='pipeline_name')
        parser.add_argument(
            '-t',
            '--transformation-config',
            help='Path to file with transformation configuration to update pipeline with.',
            type=str
        )
        parser.add_argument(
            '--config-file',
            help='Path to the pipeline updates configuration file.',
            type=str
        )

        return parser

    def do(self):
        if self.args.example_config:
            print_example_config('Pipeline Update', samples.PIPELINE_UPDATE_SAMPLE)
            return

        single_pipeline_update_args = [self.args.parameter, self.args.transformation_config]
        if not self.args.pipeline_name and not any(single_pipeline_update_args) and not self.args.config_file:
            raise Exception('Either pipeline update parameters or a configuration file must be specified.')

        if self.args.pipeline_name and not any(single_pipeline_update_args):
            raise Exception('Parameters and/or transformation config must be specified when updating a '
                            'single pipeline.')

        if not self.args.pipeline_name and any(single_pipeline_update_args):
            raise Exception('Pipeline must be specified when updating parameters and/or transformation config.')

        if (self.args.pipeline_name or any(single_pipeline_update_args)) and self.args.config_file:
            raise Exception('Both pipeline update parameters and a configuration file may not be specified. Please '
                            'specify only one option.')

        do_result = None
        # Update a single pipeline
        if self.args.pipeline_name and any(single_pipeline_update_args):
            transformation_config = None
            if self.args.transformation_config:
                if not os.path.isfile(self.args.transformation_config):
                    raise Exception('"{}" is not a file.'.format(self.args.transformation_config))

                with open(self.args.transformation_config, 'rb') as config_fh:
                    try:
                        transformation_config = config_fh.read()
                        ast.literal_eval(transformation_config)
                    except:
                        raise Exception('could not load transformation configuration from file "{}".'.format(
                            self.args.transformation_config))

            # Convert list of parameters to dict
            parameter_dict = None
            if self.args.parameter:
                parameter_dict = {param[0]: param[1] for param in self.args.parameter}

            params = {
                'pipeline_name': self.args.pipeline_name,
                'parameters': parameter_dict,
                'transformation_config': transformation_config
            }
            res = self.post_json('{hostname}/import/api/ingest/pipeline/update', data=params)
            do_result = self._handle_basic_response(res)
        else:
            # Update pipelines through a config file
            if not os.path.isfile(self.args.config_file):
                raise Exception('"{}" is not a file.'.format(self.args.config_file))
            parsed_config = None
            with open(self.args.config_file, 'rb') as config_fh:
                config_text = config_fh.read()
                try:
                    parsed_config = ast.literal_eval(config_text)
                except:
                    try:
                        parsed_config = json.loads(config_text)
                    except:
                        raise Exception('could not load configuration from file "{}".'.format(self.args.config_file))

            res = self.post_json('{hostname}/import/api/ingest/pipeline/batch_update', data=parsed_config)
            content = json.loads(res.content)
            rows = []
            if content.get('updated_pipelines'):
                rows = [[j['pipeline'], ', '.join(j['ignored_params'])] for j in content.get('updated_pipelines')]
            do_result = DoResult(entries=rows, headers=['Updated Pipelines', 'Skipped Parameters'],
                                 message='Skipped parameters are parameters not permitted to be updated. '
                                         'All other parameters were updated.')

        do_result.message = ('{}\nNOTE: All jobs for the updated pipelines must be restarted for the updates to '
                             'take effect.'.format(do_result.message))
        return do_result
