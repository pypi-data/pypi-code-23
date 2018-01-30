"""The dynamodb tool provides the ``put`` task.

The ``put`` task is used to upload json files to DynamoDB tables.  The
files to upload, and the target tables are specified in the project
configuration under the ``dynamodb`` key.

The ``targets`` sub-key, contains a mapping of name to configuration,
where each specifies ``source``, ``args``, ``table``, ``values`` and
``descrypt`` keys.


Source
------

The ``source`` key specifies a pattern to match the source files to
upload.


Table
-----

The ``table`` key specifies the table name to upload to.  Each source
file is uploaded independently to the table.

The table value is a python format string that may contain
interpolations for the args and values specified below.

The ``region_name`` key specifies the region for the table.


Arguments
---------

A directory target can be configured with ``args``, a list containing
the names of values it expects to be passed on the command line.


Values
------

The ``values`` key configures a list of names for values to be added
to the top level of the JSON before upload.

``values`` can contain names from ``args`` and the following:

project        the name of the project
branch         the current branch name
branch-slug    the current branch name, sanitised
sha            the current commit sha as a hex string
sha-mod-1024   the current as a decimal modulo 1024

The ``values`` list can also contain items of the form ``name=value``,
which will pass the var ``name`` to terraform, with the value
calculated according to ``value`` from the list above.


Decrypt
-------

The ``decrypt`` key specifies that the files matched by ``source``
should first be decrypted.  The value of the key specifies an
environment variable that holds the decryption key.

"""
import argparse
import logging
from glob import glob

import boto3

from menhir.tool import Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    changed_state,
    has_self_or_dependent_changes,
)
from menhir.utils import method, multi, select_keys

log = logging.getLogger(__name__)

REMOVE_SUBS_RE = r'%\([\w_]+\)s'


def tool():
    return DynamoDB()


class DynamoDB(Tool):

    def dir_info(tool, path, info):
        """Return a glob match on the source patterns.

        This will not be 100% accurate, but will not give false
        negatives.
        """
        import re
        from glob import glob
        files = None
        targets = info.get('dynamodb', {}).get('targets')
        if targets:
            for k, v in targets.items():
                source = v.get('source', 'config.*.json')
                source = re.sub(REMOVE_SUBS_RE, '*', source)
                files = glob(source)
        return {
            'project_recognised': False,
            'can_run': bool(files),
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build task."""
        return task(path, info, args)


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to upload JSON to dynamodb table.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="DynamoDB commands", dest='task')
    p = parsers.add_parser(
        'put',
        help='Put JSON to dynamodb'
    )
    p.add_argument('target')
    p.add_argument('--arg', action='append', dest='args')
    p.add_argument('--data-key', help="Data key to read for the data")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, args):
    return args.task


@method(task, 'put')
def task_put(path, info, args):
    changed = changed_state(info)
    if not has_self_or_dependent_changes(changed):
        log.info('dynamodb nothing to do in %s', path)
        return NOTHING_TO_DO
    config = info.get('dynamodb', {})
    targets = config.get('targets', {})
    target = args.target
    spec = targets.get(target)
    if spec is None:
        log.info('dynamodb no spec for %s in %s', target, path)
        return NOTHING_TO_DO
    data_key = args.data_key or spec.get('data-key')

    log.info('Put target: %s %s', target, args.args)
    res = put(path, info, target, args.args, data_key, spec)
    if res != OK:
        return res
    return OK


def put(path, info, target, target_args, data_key, spec):
    from os import getenv
    from menhir.tool_config import aliased_value_array

    args_names = spec.get('args', [])
    args_dict = dict(zip(args_names, target_args))

    values = spec.get('values', [])
    values_map = {
        k: v for k, v in aliased_value_array(values, info, path, args_dict)
    }

    values_and_args = args_dict.copy()
    values_and_args.update(values_map)

    table_name = spec.get('table', 'config.%(project)s')
    table_name = table_name % values_and_args
    log.debug('table_name: %s', table_name)

    decrypt = spec.get('decrypt')
    if decrypt:
        decrypt = getenv(decrypt)
        if not decrypt:
            log.error(
                'Decryption key %s specified, but not present',
                spec.get('decrypt')
            )
            return FAIL

    aws_options = {
        k: v % values_and_args
        for k, v in select_keys(values_and_args, ['region_name']).items()
    }
    log.debug('aws options: %s', aws_options)

    if data_key:
        return upload_data(info, table_name, data_key, values_map, aws_options)
    else:
        return put_file(
            path,
            spec,
            target,
            table_name,
            values_map,
            values_and_args,
            decrypt,
            aws_options,
        )


def upload_data(info, table_name, data_key, values_map, aws_options):
    data = info.get('data', {}).get(data_key)
    if data is None:
        log.error('No data available for data-key: %s', data_key)
    put_data(table_name, data, values_map, aws_options)
    return OK


def put_file(
        path, spec, target, table_name, values_map, values_and_args, decrypt,
        aws_options
):
    from json import loads
    from menhir.fileutils import load_json, load_encrypted

    source = spec.get('source', 'config.json')
    source = source % values_and_args
    files = glob(source)

    if not files:
        log.error(
            'No files match %(source)s for target %(target)s',
            {'source': source, 'target': target}
        )
        return FAIL

    for file in files:
        log.info('Uploading %s to %s', file, table_name)

        if decrypt:
            s = load_encrypted(file, decrypt)
            data = loads(s)
        else:
            print('loading ', file)
            data = load_json(file)

        res = put_data(table_name, data, values_map, aws_options)
        if res != OK:
            return res

    return OK


def put_data(table_name, data, values_map, aws_options):
    dynamodb = boto3.resource('dynamodb', **aws_options)
    table = dynamodb.Table(table_name)
    if isinstance(data, dict):
        data.update(values_map)
        log.info('Uploading item %s', data)
        table.put_item(Item=data)
    else:
        log.info('Batch writing %s', data)
        with table.batch_writer() as batch:
            for item in data:
                item.update(values_map)
                batch.put_item(Item=item)
    return OK
