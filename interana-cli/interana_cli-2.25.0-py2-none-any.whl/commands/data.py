# Copyright 2017 Interana, Inc.
'''
ia data list-delete-jobs
ia data create-delete-job
ia data remove-delete-job
'''
import ast
import json
import locale
import os
import time

from base import CommandHandler, SubCommandHandler, DoResult
from interana.utils import samples
from interana.utils.shared_parsers import add_example_config, add_output_parameters, add_run_mode
from interana.utils.command_utils import parse_config_file, print_example_config


class DataHandler(CommandHandler):

    name = 'data'
    description = 'Commands for targeted data deletion.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(DataDeleteList(),
                                  DataDeleteCreate(),
                                  DataDeleteRemove(),
                                  DataDeletePreview(),
                                  DataDeleteRun())


class DataDeleteList(SubCommandHandler):

    name = 'list-delete-jobs'
    description = 'List data delete jobs in the database.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        return parser

    def do(self):
        res = self.get('{hostname}/api/list_purge_jobs')
        content = json.loads(res.content)
        # TODO: add recurring to here if ever implemented
        if content.get('success'):
            headers = [
                'Job ID',
                'Start time',
                'End time',
                'Filters',
                'Status',
                'Create Time',
                'Update Time'
            ]
            entries = [[
                j['job_id'],
                '---' if j['start_time'] == -1 else time.strftime('%Y/%m/%d %H:%M:%S %Z',
                                                                  time.localtime(j['start_time'] / 1000)),
                '---' if j['end_time'] == -1 else time.strftime('%Y/%m/%d %H:%M:%S %Z',
                                                                time.localtime(j['end_time'] / 1000)),
                j['filters'],
                'Inactive' if j['status'] == 0 else 'Active' if j['status'] == 1 else 'Done' if j['status'] == 2
                else '---',
                '---' if j['create_time'] == -1 or j['create_time'] is None else
                time.strftime('%Y/%m/%d %H:%M:%S %Z', time.localtime(j['create_time'] / 1000)),
                '---' if j['update_time'] == -1 or j['update_time'] is None else
                time.strftime('%Y/%m/%d %H:%M:%S %Z', time.localtime(j['update_time'] / 1000)),
            ] for j in content['msg']]
        else:
            headers = ['Message', 'Success']
            entries = [[content['msg'], content['success']]]
        return DoResult(entries=entries, headers=headers)


class DataDeleteCreate(SubCommandHandler):

    name = 'create-delete-job'
    description = 'Create a data delete job based on a provided configuration file.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        add_example_config(parser)
        parser.add_argument(
          'config_file',
          help='A JSON file which specifies the data delete configuration.',
          type=str,
          nargs='?'
        )
        return parser

    def do(self):
        if self.args.example_config:
            print_example_config('Data Delete Create', samples.SELECTIVE_DELETE_CREATE_SAMPLE)
            return

        if not self.args.config_file:
            raise Exception('A data delete config file must be specified')

        parsed_config = parse_config_file(self.args.config_file)
        res = self.post_json('{hostname}/api/create_purge_job', data=parsed_config)
        return self._handle_basic_response(res)


class DataDeleteRemove(SubCommandHandler):

    name = 'remove-delete-job'
    description = 'Given an ID, remove a data delete job from the database.  Can specify multiple jobs. '\
                  'Can only remove inactive/done jobs.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='ID of jobs to be removed',
            type=int,
            nargs='+',
        )
        parser.add_argument(
            '--force',
            '-f',
            help='Remove jobs even if they are active.',
            action='store_const',
            const=1,
            default=0,
        )
        return parser

    def do(self):
        params = {'job_id': self.args.job_id, 'force': self.args.force}
        res = self.post_json('{hostname}/api/remove_purge_job', data=params)
        return self._handle_basic_response(res)


def get_config_time(config, key, default):
    try:
        return int(config.get(key))
    except TypeError:
        print 'No {} provided, using default of {}'.format(key, default)
        return default


# translates config-specified filters to AND-joined IS_ONE_OF filters
def config_to_query_filters(config_filters):
    if not isinstance(config_filters, dict) or config_filters == {}:
        raise Exception('Config must be a dict that specifies at least one filter!')

    query_filters = []
    for col_name, col_values in config_filters.iteritems():
        if not isinstance(col_values, list):
            raise Exception('"{}" filter must specify value list'.format(col_name))
        # stringify and double quote all values, then construct "IS ONE OF" filter
        values = ['(`' + col_name + '` = "' + str(value) + '")' for value in col_values]
        q_filter = '(' + 'or'.join(values) + ')'
        query_filters.append(q_filter)
    return 'AND'.join(query_filters)


class DataDeletePreview(SubCommandHandler):

    name = 'preview-delete-job'
    description = 'Preview how many events match the details specified by the '\
                  'provided configuration file.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'config_file',
            help='A JSON file which specifies the data delete configuration.',
            type=str
        )
        parser.add_argument(
            '--exact',
            help='Run an unsampled query to get an exact event count, instead '
                 'of the default sampled query for a close approximation.',
            action='store_const',
            const=True,
            default=False
        )
        return parser

    def do(self):
        # validate config file format
        parsed_config = parse_config_file(self.args.config_file)
        if not isinstance(parsed_config, dict):
            raise Exception('Config must be a dictionary')
        table_name = parsed_config.get('table_name')
        if table_name == None:
            raise Exception('Config must specify a table name')

        start_time = get_config_time(parsed_config, 'start_time', 0)
        end_time = get_config_time(parsed_config, 'end_time', int(time.time() * 1000))
        filters = config_to_query_filters(parsed_config.get('filters'))

        # create query for the external API
        params = {
            'query': json.dumps({
                'dataset': table_name,
                'start': start_time,
                'end': end_time,
                'sampled': not self.args.exact,
                'queries': [{
                    'type': 'single_measurement',
                    'measure': {
                        'aggregator': 'count_star'
                    },
                    'filter': filters
                }]
            })
        }
        res = self.get('{hostname}/api/v1/query', data=params)
        content = json.loads(res.content)
        num_events = content['rows'][0]['values'][1]

        headers = ['Number of events matching config specifications']
        locale.setlocale(locale.LC_NUMERIC, '')
        entries = [[locale.format('%d', num_events, grouping=True)]]
        return DoResult(entries=entries, headers=headers)


class DataDeleteRun(SubCommandHandler):

    name = 'run-delete-jobs'
    description = 'Mark all inactive jobs as active and ready for deletion. '\
                  'Defaults to dry-run mode.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        add_run_mode(parser)
        return parser

    def do(self):
        params = {'run': self.args.run}
        res = self.post_json('{hostname}/api/run_purge_jobs', data=params)
        return self._handle_basic_response(res)
