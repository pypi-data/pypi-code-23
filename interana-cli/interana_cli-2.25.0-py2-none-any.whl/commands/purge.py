# Copyright 2017 Interana, Inc.
'''
ia purge run
'''
from __future__ import unicode_literals

import json
import os

from base import CommandHandler, DoResult, SubCommandHandler
from interana.utils import samples
from interana.utils.shared_parsers import add_example_config, add_output_parameters, add_run_mode
from interana.utils.command_utils import parse_config_file, print_example_config


NAMED_EXPRESSION_DISPLAY_NAME = {
    'cohort': 'Cohort',
    'funnel': 'Funnel',
    'per_entity_metric': 'Per Entity Metric',
    'per_table_metric': 'Ratio Metric',
    'session': 'Session',
    'derived_column': 'Derived Column',
    'filter': 'Filter',
}

NAMED_EXPRESSION_COMPONENT_DISPLAY_NAMES = {
    'cohort': {
        'filters': 'Filters',
        'condition': 'Measure Conditions'
    },
    'funnel': {
        'global_filters': 'Global Filters',
        'states': 'Steps',
    },
    'per_entity_metric': {
        'filters': 'Filters'
    },
    'per_table_metric': {
        'numerator_filters': 'Numerator Filters',
        'denominator_filters': 'Denominator Filters'
    },
    'session': {
        'filter': 'Filters',
        'restart_filter': 'Restart Filter',
        'metrics': 'Session Metrics'
    },
    'derived_column': {
        'contents': 'Code'
    },
    'filter': {
        'filters': 'Filters'
    }
}


COMMON_NE_COMPONENT_DISPLAY_NAMES = {
    'name': 'Name',
    'persistent_name_override': 'Name Override',
    'description': 'Description'
}

DASHBOARD_CHART_COMPONENT_DISPLAY_NAMES = {
    'global_filter': 'Global Filters',
    'cache': 'Chart Cache',
    'charts': 'Charts',
    'compare_measures': 'Compare Measures',
    'compare_filters': 'Compare Filters',
    'drillstate_filters': 'Drillstate Filters',
    'basic_filter': 'Basic Filters',
    'advanced_compare': 'Advanced Compare',
    'advanced_filter': 'Advanced Filter',
    'name': 'Dashboard Name',
    'title': 'Chart Title',
    'group_labels': 'Group Labels'
}

BLOB_TYPE_DISPLAY_NAMES = {
    'charts': 'Dashboards',
    'cache': 'Dashboard Caches',
    'metadata': 'Dashboard Metadata',
    'short_url': 'Share URLs'
}


def format_ne_matches_for_display(matches, display_name_mapping, level=0):
    for field, field_results in matches.iteritems():
        field_display_name = display_name_mapping.get(field, field)
        if isinstance(field_results, dict):
            print '\t{indent}{}'.format(field_display_name, indent='\t' * level)
            format_ne_matches_for_display(field_results, display_name_mapping, level=(level + 1))
        else:
            print '\t{indent}{field}: {matches}'.format(indent='\t' * level,
                                                        field=field_display_name,
                                                        matches=', '.join([str(r) for r in field_results]))


def format_ne_result_for_display(result):
    display_name_mapping = NAMED_EXPRESSION_COMPONENT_DISPLAY_NAMES.get(result['type'])
    display_name_mapping.update(COMMON_NE_COMPONENT_DISPLAY_NAMES)
    print result['name']
    print '\tID: {}'.format(result['id'])
    print '\tName Override: {}'.format(result['persistent_name_override'])
    print '\tTable: {}'.format(result['table'])
    print '\tCreated By: {}'.format(result['created_by'])
    print '\tLast Edited By: {}'.format(result['last_edited_by'])
    print '\t-- Matches --'
    format_ne_matches_for_display(result['matches'], display_name_mapping)
    print


def format_dashboard_for_display(dashboard_result):
    print dashboard_result.get('name', '** DASHBOARD NOT FOUND DASHBOARD_METADATA **')
    print '\tID: {}'.format(dashboard_result.get('id', '** UNKNOWN **'))
    print '\tOwner: {}'.format(dashboard_result.get('owner', '** UNKNOWN **'))
    print '\t-- Matches --'

    for field, matches in dashboard_result.get('matches').iteritems():
        if field == 'charts':
            for _, chart_res in matches.iteritems():
                print '\t{}'.format(chart_res.get('title'))
                format_ne_matches_for_display(chart_res['matches'], DASHBOARD_CHART_COMPONENT_DISPLAY_NAMES, level=1)
        else:
            print '\t{}: {}'.format(DASHBOARD_CHART_COMPONENT_DISPLAY_NAMES.get(field, field),
                                    ', '.join([str(m) for m in matches]))


def format_dashboard_metadata_for_display(blob_result):
    print blob_result['id']
    print '\t-- Matches --'
    for name, res in blob_result.get('matches', {}).iteritems():
        print '\t{}'.format(name)
        for field, matches in res.iteritems():
            print '\t\t{}: {}'.format(DASHBOARD_CHART_COMPONENT_DISPLAY_NAMES.get(field, field),
                                      ', '.join([str(m) for m in matches]))


def format_shorturl_for_display(blob_result):
    print blob_result['id']
    print '\t-- Matches -- '
    format_ne_matches_for_display(blob_result.get('matches', {}), DASHBOARD_CHART_COMPONENT_DISPLAY_NAMES)


def format_blob_for_display(blob_type, blob_result):
    if blob_type == 'charts':
        format_dashboard_for_display(blob_result)
    elif blob_type == 'metadata':
        format_dashboard_metadata_for_display(blob_result)
    elif blob_type == 'short_url':
        format_shorturl_for_display(blob_result)
    print


def format_sfe_for_display(sfe_result):
    output = '\t{} - '.format(sfe_result['id'])
    if sfe_result.get('name'):
        output += 'Name: {} '.format(sfe_result.get('name'))
    if sfe_result.get('value'):
        output += 'Value: {}'.format(sfe_result.get('value'))
    print output


def display_metadata_results(metadata_results):
    print '\n----- Metadata Results -----\n'
    if metadata_results.get('named_expressions'):
        for ne_table, ne_results in metadata_results.get('named_expressions').iteritems():
            print '{}'.format(NAMED_EXPRESSION_DISPLAY_NAME.get(ne_table))
            print '********************\n'
            for ne_res in ne_results:
                format_ne_result_for_display(ne_res)
        print
    if metadata_results.get('blobs'):
        for blob_type, blob_results in metadata_results.get('blobs').iteritems():
            print '{}'.format(BLOB_TYPE_DISPLAY_NAMES.get(blob_type))
            print '********************\n'
            for blob_res in blob_results:
                format_blob_for_display(blob_type, blob_res)
            print
        print
    if metadata_results.get('shard_function_exceptions'):
        print 'Shard Function Exceptions'
        print '********************\n'
        for table, tc_results in metadata_results.get('shard_function_exceptions').iteritems():
            print table
            for table_copy, e_results in tc_results.iteritems():
                print '\t{}'.format(table_copy)
                print '\t-- Matches --'
                for e_res in e_results:
                    format_sfe_for_display(e_res)
                print


class PurgeHandler(CommandHandler):

    name = 'purge'
    description = 'Commands for privacy purge.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(PurgeRun())


class PurgeRun(SubCommandHandler):

    name = 'run'
    description = 'Deletes strings, events, and metadata with values specified '\
                  'by the provided file. Defaults to dry-run mode.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_example_config(parser)
        add_output_parameters(parser)
        parser.add_argument(
            'config_file',
            help='A JSON file which specifies the purge configuration',
            type=str,
            nargs='?'
        )
        add_run_mode(parser)
        return parser

    def do(self):
        if self.args.example_config:
            print_example_config('Purge Create', samples.PURGE_CREATE_SAMPLE)
            return

        if not self.args.config_file:
            raise Exception('A purge config file must be specified')

        parsed_config = parse_config_file(self.args.config_file)
        params = {'dry_run': 0 if self.args.run else 1}
        res = self.post_json('{hostname}/api/run_purge', data=parsed_config, params=params)

        content = json.loads(res.content)

        display_metadata_results(content.get('data', {}).get('metadata', {}))
        return DoResult(message=content['msg'])
