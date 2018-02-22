from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
import os
from subprocess import check_call
import tempfile

import pkg_resources

from . import data_lookup
from .structures import DiracFile
from .data_management import loookup_replicas
from .data_management import mirror_files
from .utils import dump


def add_input_data_subparser(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument('--production-id', default=None)
    group.add_argument('--bk-path', default=None)
    group.add_argument('--lfns', nargs='+', default=None)
    group.add_argument('--lfns-fn', default=None)
    # group.add_argument('--batch', default=None)
    group.add_argument('--ganga-jid', default=None)
    return group


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    lookup_parser = subparsers.add_parser('lookup')
    lookup_parser.add_argument('--output-fn', required=True)
    add_input_data_subparser(lookup_parser)
    lookup_parser.set_defaults(func=lookup)

    mirror_parser = subparsers.add_parser('mirror')
    mirror_parser.add_argument('--mirror-dir', required=True)
    add_input_data_subparser(mirror_parser)
    mirror_parser.set_defaults(func=mirror)

    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument('--merged-fn', required=True)
    add_input_data_subparser(merge_parser)
    merge_parser.set_defaults(func=merge)

    args = parser.parse_args()
    args.func(args)


def _get_lfns_from_args(args):
    if args.bk_path:
        print('Getting LFNs from:', args.bk_path)
        return data_lookup.from_bkquery(args.bk_path)

    if args.lfns_fn:
        with open(args.lfns_fn, 'rt') as fp:
            return [DiracFile(lfn.strip()) for lfn in fp.read().split('\n')]
    elif args.lfns:
        if isinstance(args.lfns, list):
            return [DiracFile(lfn) for lfn in args.lfns]
        else:
            return [DiracFile(args.lfns)]

    if args.ganga_jid:
        print('Getting LFNs from ganga job:', args.ganga_jid)
        output_fn = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name
        script_fn = tempfile.NamedTemporaryFile(suffix='.py', delete=False).name
        script = pkg_resources.resource_string(__name__, 'templates/get_job_from_ganga.py')
        script = script.replace('{{j_id}}', str(args.ganga_jid))
        script = script.replace('{{output_fn}}', output_fn)
        with open(script_fn, 'wt') as fp:
            fp.write(script)
        check_call(' '.join(['ganga', '--no-mon', script_fn]), shell=True)
        with open(output_fn, 'rt') as fp:
            result = json.load(fp)
        if 'error' in result:
            raise RuntimeError(result['error'])
        return [DiracFile(lfn) for lfn in result['lfns']]

    raise NotImplementedError(args)


def lookup(args):
    files = _get_lfns_from_args(args)
    loookup_replicas(files)
    dump(files, args.output_fn)


def mirror(args):
    files = _get_lfns_from_args(args)
    loookup_replicas(files)
    mirror_files(files, args.mirror_dir)


def merge(args):
    files = _get_lfns_from_args(args)
    loookup_replicas(files)
    pfns = [str(f.replicas[0].pfn) for f in files if f.replicas]
    assert len(pfns) > 0, 'Failed to get any files?'
    if len(pfns) != len(files):
        print('WARNING: Merging', len(pfns), 'out of', len(files), 'files')
    command = ' '.join(['lb-run', 'ROOT', 'hadd', '-fk', args.merged_fn] + pfns)
    if len(command) > os.sysconf('SC_ARG_MAX'):
        print(command)
        raise ValueError('Command too long')
    check_call(command, shell=True)


if __name__ == '__main__':
    parse_args()
