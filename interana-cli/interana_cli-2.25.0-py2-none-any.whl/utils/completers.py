# Copyright 2017 Interana, Inc.
import json


class ApiFetchCompleter(object):
    '''Base class for completers that query the API'''

    def __init__(self, command):
        self.c = command


class TablesCompleter(ApiFetchCompleter):
    '''tab-completes names of all tables, unless specified otherwise'''

    def __init__(self, command, type='all'):
        assert (type in {'all', 'event', 'lookup'})  # no other types are allowed
        super(TablesCompleter, self).__init__(command)
        self.type = type

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/get_tables', params={'type': self.type})
        tables = json.loads(res.content)
        names = (t['table_name'] for t in tables['tables'])
        return (n for n in names if n.startswith(prefix))


class ShardKeyCompleter(ApiFetchCompleter):
    '''tab-completes names of shard_keys of tables'''

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/get_tables')
        tables = json.loads(res.content)['tables']
        table_name = self.c.args_dict['table_name']
        for table in tables:
            if table['table_name'] == table_name:
                shard_keys = table['shard_keys']
                break

        return (shard_key for shard_key in shard_keys if shard_key.startswith(prefix))


class ColumnsCompleter(ApiFetchCompleter):
    '''tab-completes names of columns of table'''

    def __init__(self, command, show_hidden=False, table_name_arg='table_name'):
        assert (show_hidden in {True, False})
        super(ColumnsCompleter, self).__init__(command)
        self.show_hidden = show_hidden
        self.table_name_arg = table_name_arg

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        table_name = self.c.args_dict[self.table_name_arg]
        res = self.c.get('{hostname}/import/api/get_table_columns',
                         params={'table_name': table_name, 'show_hidden': int(self.show_hidden)})
        content = json.loads(res.content)
        names = (c['name'] for c in content['columns'])
        results = (n for n in names if n.startswith(prefix))
        return results


class PipelinesCompleter(ApiFetchCompleter):
    '''tab-completes names of pipelines'''

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/pipelines/readall')
        pipelines = json.loads(res.content)
        names = (p['pipeline_name'] for p in pipelines['pipelines'])
        return (n for n in names if n.startswith(prefix))


class TransformerTypesCompleter(ApiFetchCompleter):

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/transformers/list_types')
        types = json.loads(res.content)
        type_names = (t['transformer_type_name'] for t in types['types'])
        return (n for n in type_names if n.startswith(prefix))


class SettingsApplicationCompleter(ApiFetchCompleter):

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/api/get_setting_apps')
        applications = json.loads(res.content)['applications']
        return (a for a in applications if a.startswith(prefix))


class SettingsKeyCompleter(ApiFetchCompleter):

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        application = self.c.args_dict['application']
        res = self.c.get('{hostname}/api/get_setting_keys',
                         params={'application': application})
        keys = json.loads(res.content)['keys']
        return (k for k in keys if k.startswith(prefix))


class DataSourceTypeCompleter(ApiFetchCompleter):
    '''tab-completes names of data source types'''

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/pipelines/list_types')
        data_source_types = json.loads(res.content)
        names = (dst['data_source_name'] for dst in data_source_types['types'])
        return (n for n in names if n.startswith(prefix))


class PipelineParameterCompleter(ApiFetchCompleter):
    '''tab-completes names of pipeline parameters'''

    def __init__(self, command, query_parameter='data_source_type'):
        assert (query_parameter in {'data_source_type', 'pipeline_name', 'pipeline_id', 'pipeline', 'job_id'})
        super(PipelineParameterCompleter, self).__init__(command)
        self.query_parameter = query_parameter

    def _is_int(self, value):
        is_int = False
        if isinstance(value, int):
            is_int = value > 0
        else:
            try:
                is_int = int(value) > 0
            except:
                pass
        return is_int

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        params = {}
        if self.query_parameter == 'pipeline':
            pipeline_param = self.c.args_dict.get(self.query_parameter)
            if self._is_int(pipeline_param):
                params['pipeline_id'] = pipeline_param
            else:
                params['pipeline_name'] = pipeline_param
        else:
            params[self.query_parameter] = self.c.args_dict.get(self.query_parameter)

        res = self.c.post_json('{hostname}/import/api/ingest/pipeline/list_parameters', data=params)
        content = json.loads(res.content)
        return (n for n in content['parameters'] if n.startswith(prefix))


class ImportNodesCompleter(ApiFetchCompleter):
    '''tab-completes names of all import nodes, unless specified otherwise'''

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/ingest/list_import_nodes')
        content = json.loads(res.content)
        return (n for n in content['parameters'] if n.startswith(prefix))


class DateTimeFormatCompleter(ApiFetchCompleter):
    '''tab-completes datetime formats for datetime columns'''

    def __call__(self, prefix, parsed_args, **kwargs):
        self.c.initialize(parsed_args)
        res = self.c.get('{hostname}/import/api/get_time_formats')
        content = json.loads(res.content)
        return (n['format_string'] for n in content['formats'] if n['format_string'].startswith(prefix))
