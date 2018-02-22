# Copyright 2017 Interana, Inc.
'''
ia column list
ia column update
ia column delete
'''

import json
from base import CommandHandler, DeleteBase, DoResult, SubCommandHandler
from ..utils.completers import ColumnsCompleter, DateTimeFormatCompleter, TablesCompleter
from ..utils.shared_parsers import add_output_parameters, add_run_mode

supported_types = ['int', 'identifier', 'decimal', 'dollars', 'int_set', 'string_set', 'string',
                   'url', 'ip', 'user_agent', 'seconds', 'milliseconds', 'microseconds', 'datetime']


class ColumnHandler(CommandHandler):

    name = 'column'
    description = 'Commands for managing columns.'

    def __init__(self):
        CommandHandler.__init__(self)

        self.register_subcommands(ColumnList(),
                                  ColumnUpdate(),
                                  ColumnDelete(),
                                  ColumnHide(),
                                  ColumnUnhide(),
                                  ColumnExcludeImport(),
                                  ColumnIncludeImport())


class ColumnList(SubCommandHandler):

    name = 'list'
    description = 'List columns.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Name of the table.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            '-t',
            '--type',
            help='Show a specified type of columns.',
            type=str,
            choices=['all', 'deleted', 'hidden', 'import-excluded'],
        )

        return parser

    def do(self):
        params = {
            'table_name': self.args.table_name
        }
        if self.args.type is None:
            pass  # show active (not hidden, not omitted) columns
        elif self.args.type == 'all':
            params['show_hidden'] = 'any'
        elif self.args.type == 'deleted':
            params['show_hidden'] = 1
            params['show_omit'] = 1
        elif self.args.type == 'hidden':
            params['show_hidden'] = 1
            params['show_omit'] = 0
        elif self.args.type == 'import-excluded':
            params['show_hidden'] = 0
            params['show_omit'] = 1
        else:
            raise Exception('"{}" is not a supported --show value'.format(self.args.type))

        res = self.get('{hostname}/import/api/get_table_columns', params=params)
        columns = json.loads(res.content)['columns']

        headers = ['Column ID',
                   'Table ID',
                   'Col Name',
                   'Friendly Name',
                   'Shard Key',
                   'Type',
                   'Conversion Params',
                   'Attributes',
                   ]
        entries = [[
            r['column_id'],
            r['table_id'],
            r['name'],
            r['full_name'],
            'X' if bool(r['shard_key']) else '',
            r['friendly_type'],
            r['conversion_function_params'],
            r['attributes'],
        ] for r in columns]

        return DoResult(
            entries=entries,
            headers=headers
        )


class ColumnUpdate(SubCommandHandler):

    name = 'update'
    description = 'Update an existing column. Currently only supports changing column types.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to change.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to change.',
            type=str
        ).completer = ColumnsCompleter(self)
        parser.add_argument(
            '-t',
            '--type',
            help='New type for column.',
            type=str,
            choices=supported_types,
            required=True
        )
        parser.add_argument(
            '--keep-old-column',
            help='Keep the old data and strings of the column being changed instead of deleting them.',
            action='store_true'
        )
        parser.add_argument(
            '--identifier-digits',
            type=int,
            help='Number of digits of the identifier (hex) column data. '
            'Required when changing to identifier type and must be a multiple of 8.',
            default=0
        )
        parser.add_argument(
            '--datetime-format',
            type=str,
            help='Python-style datetime format for datetime columns. Example: "%%Y-%%m-%%d %%H:%%M:%%S".'
        ).completer = DateTimeFormatCompleter(self)
        add_run_mode(parser)

        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        if self.args.keep_old_column:
            full_delete = 0
        else:
            full_delete = 1

        # If attempting conversion to identifier without not providing hex digits, raise exception
        assert not (self.args.type == 'identifier' and not self.args.identifier_digits),\
            "Identifier digits (--identifier-digits) must be provided for identifier conversion"

        # If attempting conversion to datetime without providing datetime format, raise exception
        assert not (self.args.type == 'datetime' and not self.args.datetime_format),\
            "Datetime format (--datetime-format) must be provided for the datetime type"

        post_data = {'table_name': table_name, 'column_name': column_name,
                     'conversion_function': self.args.type, 'full_delete': full_delete,
                     'revert': False, 'run': self.args.run, 'hex_digits': self.args.identifier_digits,
                     'time_format': self.args.datetime_format, 'use_friendly_names': 1}
        res = self.post('{hostname}/import/api/change_column_type', data=post_data)
        content = json.loads(res.content)
        headers = ['Table', 'Column', 'Old type', 'New type']
        entries = [[content['table_name'], content['column_name'], content['old_conversion_function'],
                    content['conversion_function']]]
        if self.args.run:
            next_action = "The changes have been committed."
        else:
            next_action = "This is a preview mode. Rerun with --run option for changes to take effect."
        return DoResult(
            entries=entries,
            headers=headers,
            message=next_action
        )


class ColumnDelete(DeleteBase):

    name = 'delete'
    description = 'Delete a column. Does NOT delete metadata by default.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to delete.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to delete. Required if not using match-pattern.',
            type=str,
            nargs='?'
        ).completer = ColumnsCompleter(self)
        parser.add_argument(
            '--match-pattern',
            type=str,
            help='Delete all columns in table matching the given pattern, using SQL pattern matching.',
        )
        parser.add_argument(
            '--delete-metadata',
            help='Delete both column metadata and data.',
            action='store_const',
            const=1,
            default=0,
        )
        add_run_mode(parser)

        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        match_pattern = self.args.match_pattern
        if not match_pattern and not column_name:
            raise Exception('If not pattern matching using match-pattern, column name must be specified.')
        if match_pattern and column_name:
            raise Exception('If using match-pattern, column_name argument must be empty.')

        if self.args.delete_metadata:
            full_delete = 1
            print 'Column metadata will be deleted and no longer exist in the UI.\n'
        else:
            full_delete = 0
            print 'Column metadata will NOT be deleted and will continue to exist in the UI.\n'
        run = self.args.run

        if match_pattern:
            where_clause = json.dumps([["name", match_pattern]])
            post_data = {
                'table_name': table_name,
                'where_clause': where_clause,
                'full_delete': full_delete
            }
            if self.args.run:
                res = self.post('{hostname}/import/api/column_sql_delete', data=post_data)
                content = json.loads(res.content)
                columns_deleted = [[str(cn)] for cn in content['column_names']]
            else:
                res = self.post('{hostname}/import/api/test_column_sql', data=post_data)
                content = json.loads(res.content)
                columns_deleted = [[str(column['name'])] for column in content['column_info']]

        else:
            post_data = {
                'table_name': table_name,
                'column_name': column_name,
                'full_delete': full_delete,
                'run': run
            }
            res = self.post('{hostname}/import/api/delete_column', data=post_data)
            content = json.loads(res.content)
            columns_deleted = [[cn] for cn in content['column_names']]

        headers = ['Columns deleted'] if self.args.run else ['Columns to be deleted']
        entries = columns_deleted

        if not columns_deleted:
            next_action = 'No columns were found matching the given pattern.'
        elif run:
            next_action = 'The changes have been committed.'
        else:
            next_action = 'This is a preview mode. Rerun with --run option for changes to take effect.'

        return DoResult(headers=headers, entries=entries, message=next_action)


class ColumnHide(SubCommandHandler):

    name = 'hide'
    description = 'Hide a column from the UI.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to hide.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to hide.',
            type=str,
        ).completer = ColumnsCompleter(self)
        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        post_data = {
            'table_name':  table_name,
            'column_name': column_name,
            'unhide': False
        }
        res = self.post('{hostname}/import/api/hide_column', data=post_data)
        print ('Note: Hidden column is not deleted and continues receiving data.  To show the column again, '
               'run "ia column unhide" command.')
        return self._handle_basic_response(res)


class ColumnUnhide(SubCommandHandler):

    name = 'unhide'
    description = 'Unhide a column hidden from the UI.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to unhide.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to unhide.',
            type=str,
        ).completer = ColumnsCompleter(self, show_hidden=True)
        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        post_data = {
            'table_name':  table_name,
            'column_name': column_name,
            'unhide': True
        }
        res = self.post('{hostname}/import/api/hide_column', data=post_data)
        return self._handle_basic_response(res)


class ColumnExcludeImport(SubCommandHandler):

    name = 'exclude-import'
    description = 'exclude column from import.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to exclude from import.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to exclude from import.',
            type=str,
        ).completer = ColumnsCompleter(self)
        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        post_data = {
            'table_name':  table_name,
            'column_name': column_name,
            'unomit': False
        }
        res = self.post('{hostname}/import/api/omit_column', data=post_data)
        return self._handle_basic_response(res)


class ColumnIncludeImport(SubCommandHandler):

    name = 'include-import'
    description = 'include column into import.'

    def parser_setup(self, sps):
        parser = self.init_parser(sps)
        add_output_parameters(parser)
        parser.add_argument(
            'table_name',
            help='Table containing column to include into import.',
            type=str
        ).completer = TablesCompleter(self)
        parser.add_argument(
            'column_name',
            help='Column to include into import.',
            type=str,
        ).completer = ColumnsCompleter(self)
        return parser

    def do(self):
        table_name = self.args.table_name
        column_name = self.args.column_name
        post_data = {
            'table_name':  table_name,
            'column_name': column_name,
            'unomit': True
        }
        res = self.post('{hostname}/import/api/omit_column', data=post_data)
        return self._handle_basic_response(res)
