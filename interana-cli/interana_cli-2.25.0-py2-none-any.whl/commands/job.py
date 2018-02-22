# Copyright 2017 Interana, Inc.
'''
ia job create
ia job read
ia job stats
ia job list
ia job pause
ia job resume
ia job delete
ia job update
ia job export

ia pipeline create "test_table" "jpipe" aws
ia transformer create jtpipe" "xz"

ia job create jtpipe yesterday today

ia job read 1

ia job list
ia job list all
ia job list done

ia job update 1 --start_day 2000-01-01

ia job delete 1
'''

from base import CommandHandler, SubCommandHandler, DoResult
from ..utils.completers import ImportNodesCompleter, PipelinesCompleter, PipelineParameterCompleter, TablesCompleter
from ..utils.shared_parsers import add_output_parameters, add_run_mode
from ..utils.command_utils import parse_ingest_input_date, IngestInputDate

from collections import OrderedDict

import ast
import datetime
import json
import os

_statuses = {
    'inactive': 0,
    'active': 1,
    'done': 2,
    'paused': 3
}

_forevers = {
    'one_time': 0,
    'forever': 1,
}


class JobHandler(CommandHandler):

    name = 'job'
    description = 'Commands for managing ingest jobs.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(JobCreate(),
                                  JobUpdate(),
                                  JobList(),
                                  JobPause(),
                                  JobResume(),
                                  JobDelete(),
                                  JobStats())


class JobUpdate(SubCommandHandler):

    name = 'update'
    description = 'Update an existing job\'s parameters, start date, etc.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='ID of job to update.',
            type=int,
        )
        parser.add_argument(
            '-s',
            '--start',
            help='Start date for the job.',
            type=str,
        )
        parser.add_argument(
            '-e',
            '--end',
            help='End date for the job.',
            type=str,
        )
        parser.add_argument(
            '--nodes',
            '-n',
            help='Use to specify which import nodes to run this job on. '
                 'Use "all" or list specific nodes, i.e. "import000 import001".',
            nargs='+'
        ).completer = ImportNodesCompleter(self)
        parser.add_argument(
            '-o',
            '--override',
            help='Adds or updates an override of a pipeline parameter for the specified job. '
                 'Specify parameter name and value to override. '
                 'Can be specified multiple times to update multiple parameters.',
            nargs=2,
            metavar=('PARAMETER_NAME', 'VALUE'),
            action='append'
        ).completer = PipelineParameterCompleter(self, query_parameter='job_id')
        parser.add_argument(
            '--remove-override',
            help='Removes an override of a pipeline parameter for the specified job. '
                 'Specify parameter name to remove. '
                 'Can be specified multiple times to remove multiple parameters.',
            metavar=('PARAMETER_NAME'),
            action='append'
        ).completer = PipelineParameterCompleter(self, query_parameter='job_id')

        return parser

    def do(self):
        if not self.args.start and not self.args.end and not self.args.nodes \
                and not self.args.override and not self.args.remove_override:
            raise Exception('At least one change needs to be specified.')

        # Convert list of overrides to dict; remove_override is already a list so need to parse that
        override_dict = None
        if self.args.override:
            override_dict = {param[0]: param[1] for param in self.args.override}
            if self.args.remove_override:
                for override in self.args.remove_override:
                    if override in override_dict:
                        raise Exception('Cannot set override "{}" and remove it at the same time.'.format(override))

        if self.args.remove_override:
            self.args.remove_override = list(set(self.args.remove_override))  # dedup entries

        params = {
            'job_id': self.args.job_id,
            'start_day': self.args.start,
            'until_day': self.args.end,
            'job_overrides': json.dumps(override_dict),
            'remove_job_overrides': json.dumps(self.args.remove_override)
        }
        if self.args.nodes:
            if isinstance(self.args.nodes, list):
                params['run_on_selected_nodes'] = ','.join(self.args.nodes)
            else:
                params['run_on_selected_nodes'] = self.args.nodes

        res = self.post('{hostname}/import/api/job/update', data=params)
        content = json.loads(res.content)

        # parse response; same as job_list, except it's just one item
        table_columns = [
            ('job_id', 'Job ID'),
            ('pipeline_id', 'Pipeline ID'),
            ('name', 'Pipeline Name'),
            ('table', 'Table'),
            ('type', 'Type'),
            ('start', 'Start'),
            ('end', 'End'),
            ('status', 'Status'),
            ('running_import_nodes', 'Running Import Nodes'),
            ('overrides', 'Overrides'),
        ]
        entries = [[content[f[0]] for f in table_columns]]

        return DoResult(entries=entries, headers=[tc[1] for tc in table_columns])


class JobPause(SubCommandHandler):

    name = 'pause'
    description = 'Pause a running ingest job. Can specify multiple jobs.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='IDs of jobs to be paused.',
            type=int,
            nargs='*',
        )
        parser.add_argument(
            '-p',
            '--pipeline',
            help='Name of pipelines to which jobs belong. Can specify multiple pipelines.',
            type=str,
            nargs='+'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-a',
            '--all',
            help='Pause all running jobs.',
            action='store_const',
            const=1,
            default=0,
        )
        parser.add_argument(
            '-t',
            '--table',
            help='Pause all active jobs for the table.',
            type=str,
        ).completer = TablesCompleter(self)

        return parser

    def do(self):
        if sum(1 for p in [self.args.job_id, self.args.pipeline, self.args.all, self.args.table] if p) != 1:
            raise Exception('Exactly one of  --all, --table, --pipeline, or job_id must be specified')

        params = {
            'job_ids': self.args.job_id,
            'pipeline_names': self.args.pipeline,
            'action': 'pause',
            'all': self.args.all,
            'table': self.args.table
        }
        res = self.post_json('{hostname}/import/api/ingest/toggle_job_status', data=params)
        return self._handle_basic_response(res)


class JobResume(SubCommandHandler):

    name = 'resume'
    description = 'Resume a paused ingest job. Can specify multiple jobs.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='IDs of jobs to be paused.',
            type=int,
            nargs='*',
        )
        parser.add_argument(
            '-p',
            '--pipeline',
            help='Name of pipelines to which jobs belong. Can specify multiple pipelines.',
            type=str,
            nargs='+'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-a',
            '--all',
            help='Resume all paused jobs.',
            action='store_const',
            const=1,
            default=0,
        )
        parser.add_argument(
            '-t',
            '--table',
            help='Resume all paused jobs for the table.',
            type=str,
        ).completer = TablesCompleter(self)
        return parser

    def do(self):
        if sum(1 for p in [self.args.job_id, self.args.pipeline, self.args.all, self.args.table] if p) != 1:
            raise Exception('Exactly one of  --all, --table, --pipeline, or job_id must be specified')

        params = {
            'job_ids': self.args.job_id,
            'pipeline_names': self.args.pipeline,
            'action': 'resume',
            'all': self.args.all,
            'table': self.args.table
        }
        res = self.post_json('{hostname}/import/api/ingest/toggle_job_status', data=params)
        return self._handle_basic_response(res)


class JobDelete(SubCommandHandler):

    name = 'delete'
    description = 'Delete an ingest job. Can specify multiple jobs.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='IDs of jobs to be paused.',
            type=int,
            nargs='*',
        )
        parser.add_argument(
            '-p',
            '--pipeline',
            help='Name of pipelines to which jobs belong. Can specify multiple pipelines.',
            type=str,
            nargs='+'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-a',
            '--all',
            help='Delete all running and paused jobs.',
            action='store_const',
            const=1,
            default=0,
        )
        parser.add_argument(
            '-t',
            '--table',
            help='Pause all running and paused jobs for the table.',
            type=str,
        ).completer = TablesCompleter(self)
        add_run_mode(parser)

        return parser

    def do(self):
        if sum(1 for p in [self.args.job_id, self.args.pipeline, self.args.all, self.args.table] if p) != 1:
            raise Exception('Exactly one of  --all, --table, --pipeline, or job_id must be specified')

        params = {
            'job_ids': self.args.job_id,
            'pipeline_names': self.args.pipeline,
            'action': 'delete',
            'all': self.args.all,
            'table': self.args.table,
            'run': self.args.run
        }
        res = self.post_json('{hostname}/import/api/ingest/toggle_job_status', data=params)
        if not self.args.run:
            print "This is preview mode, the following changes are what would happen if --run/-r was used."
        return self._handle_basic_response(res)


class JobList(SubCommandHandler):

    name = 'list'
    description = 'List ingest jobs. Can filter based on status, table, and type.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            '-p',
            '--pipeline',
            help='Name of pipelines to which jobs belong. Can specify multiple pipelines.',
            type=str,
            nargs='+'
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            '-s',
            '--status',
            help='List jobs with a specific status.',
            choices=['running', 'paused', 'done'],
            type=str,
        )
        parser.add_argument(
            '--table',
            help='List jobs for the given table.',
            type=str,
        ).completer = TablesCompleter(self)
        parser.add_argument(
            '-t',
            '--type',
            help='List jobs of the specified type.',
            choices=['continuous', 'onetime'],
            type=str,
        )

        return parser

    def do(self):
        params = {
            'pipeline': self.args.pipeline,
            'status': self.args.status,
            'table': self.args.table,
            'type': self.args.type
        }
        res = self.post_json('{hostname}/import/api/ingest/list_jobs', data=params)
        content = json.loads(res.content)

        table_columns = [
            ('job_id', 'Job ID'),
            ('pipeline_id', 'Pipeline ID'),
            ('name', 'Pipeline Name'),
            ('table', 'Table'),
            ('type', 'Type'),
            ('start', 'Start'),
            ('end', 'End'),
            ('status', 'Status'),
            ('running_import_nodes', 'Running Import Nodes'),
            ('overrides', 'Overrides'),
        ]
        entries = [[r[f[0]] for f in table_columns] for r in content.get('jobs', [])]

        table_msg = " for table '{}'".format(self.args.table) if self.args.table else ""
        type_msg = " of type '{}'".format(self.args.type) if self.args.type else ""
        status_msg = " with status '{}'".format(self.args.status) if self.args.status else ""
        empty_warning = "No jobs{}{}{} were found.".format(table_msg, type_msg, status_msg)

        return DoResult(entries=entries, headers=[tc[1] for tc in table_columns], empty_warning=empty_warning)


class JobStats(SubCommandHandler):

    name = 'stats'
    description = ('Display stats for a job. Stats include file count, total raw file sizes, total transformed '
                   'file sizes, and total line count and are grouped by date. A date range may be specified, '
                   'but if not specified, continuous jobs will display stats from their scan window, and '
                   'onetime jobs will display their entire date range.')

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'job_id',
            help='ID of job to get stats for',
            type=int
        )
        parser.add_argument(
            '-s',
            '--start',
            help='Start of date range of stats to retrieve (inclusive). Date must be in '
            'YYYY-MM-dd or YYYY-MM-ddTHH:mm:ss formats.',
            type=IngestInputDate
        )
        parser.add_argument(
            '-e',
            '--end',
            help='End of date range of stats to retrieve (inclusive). Date must be in '
            'YYYY-MM-dd or YYYY-MM-ddTHH:mm:ss formats.',
            type=IngestInputDate
        )
        return parser

    def do(self):
        date_range_args = (self.args.start, self.args.end)
        if any(date_range_args) and not all(date_range_args):
            raise Exception('When specifying a date range, both start and end must be specified')

        if all(date_range_args):
            validated_start = parse_ingest_input_date(self.args.start)
            validated_end = parse_ingest_input_date(self.args.end)
            if not validated_start:
                raise Exception('Invalid start time: {}'.format(self.args.start))
            if not validated_end:
                raise Exception('Invalid end time: {}'.format(self.args.end))
            if validated_end < validated_start:
                raise Exception("End time '{}' cannot be earlier than start time '{}'."
                                .format(self.args.end, self.args.start))

        params = {
            'job_id': self.args.job_id,
            'start': self.args.start,
            'end': self.args.end
        }
        res = self.post_json('{hostname}/import/api/ingest/job_stats', data=params)
        content = json.loads(res.content)

        table_columns = [
            ('iteration_date', 'Date'),
            ('status', 'Status'),
            ('file_count', 'Files'),
            ('total_raw_size', 'Raw File Size'),
            ('total_transformed_size', 'Transformed File Size'),
            ('total_line_count', 'Line Count')
        ]
        entries = [[r[f[0]] for f in table_columns] for r in content.get('stats', [])]

        empty_warning = ("No statistics were found for id {}. It likely did not import anything yet "
                         "(during the timerange if specified).".format(self.args.job_id))
        return DoResult(entries=entries, headers=[tc[1] for tc in table_columns], empty_warning=empty_warning)


class JobCreate(SubCommandHandler):

    name = 'create'
    description = 'Create a new ingest job for an existing dataset with options.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'pipeline',
            help='Pipeline name or ID to create a job for.',
            type=str
        ).completer = PipelinesCompleter(self)
        parser.add_argument(
            'type',
            help='Type of job to be created.',
            type=str,
            choices=['continuous', 'onetime']
        )
        parser.add_argument(
            '--paused',
            '-p',
            help='Create the job as paused.',
            action='store_const',
            const=1,
            default=0,
        )

        parser.add_argument(
            'start',
            help='Start date for job.',
            type=IngestInputDate
        )
        parser.add_argument(
            'end',
            help='End date for job.',
            type=IngestInputDate
        )
        parser.add_argument(
            '--nodes',
            '-n',
            help='Use to specify which import nodes to run this job on. '
                 'Use "all" or list specific nodes, i.e. "import000 import001".',
            type=str,
            nargs='+',
            default=['all'],
            required=False
        ).completer = ImportNodesCompleter(self)
        parser.add_argument(
            '-o',
            '--override',
            help='Pipeline parameter and value to override for job configuration. '
            'Can be specified multiple times to update multiple parameters.',
            type=str,
            nargs=2,
            metavar=('PARAMETER_NAME', 'VALUE'),
            action='append'
        ).completer = PipelineParameterCompleter(self, query_parameter='pipeline')

        return parser

    def do(self):
        job_config = {}
        if self.args.pipeline.isdigit():
            job_config['pipeline_id'] = int(self.args.pipeline)
        else:
            job_config['pipeline_name'] = self.args.pipeline

        job_config['continuous'] = 1 if self.args.type == 'continuous' else 0
        job_config['status'] = 'paused' if self.args.paused else 'active'
        job_config['start'] = self.args.start
        job_config['end'] = self.args.end

        if self.args.nodes:
            job_config['running_import_nodes'] = self.args.nodes
        if self.args.override:
            job_config['overrides'] = {param[0]: param[1] for param in self.args.override}

        res = self.post_json('{hostname}/import/api/ingest/create_job', data=job_config)
        content = json.loads(res.content)

        table_columns = [
            ('job_id', 'Job ID'),
            ('pipeline_id', 'Pipeline ID'),
            ('name', 'Pipeline Name'),
            ('table', 'Table'),
            ('type', 'Type'),
            ('start', 'Start'),
            ('end', 'End'),
            ('status', 'Status'),
            ('running_import_nodes', 'Running Import Nodes'),
            ('overrides', 'Overrides')
        ]
        entries = [[r[f[0]] for f in table_columns] for r in content.values()]
        empty_warning = "Job could not be created."
        return DoResult(entries=entries, headers=[tc[1] for tc in table_columns],
                        empty_warning=empty_warning)
