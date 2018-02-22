from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import json
from os.path import join
import re

from .data_management import lookup_files_from_query
from .data_management import loookup_replicas
from .data_management import mirror_files
from .utils import dump


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    mirror_parser = subparsers.add_parser('lookup')
    mirror_parser.add_argument('--mirror-dir', required=False)
    mirror_parser.add_argument('--output-fn', default=None)
    group = mirror_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--production-id', default=None)
    group.add_argument('--bk-path', default=None)
    group.add_argument('--lfns', nargs='+', default=None)
    group.add_argument('--lfns-fn', default=None)
    group.add_argument('--batch', default=None)
    mirror_parser.set_defaults(func=lambda a: lookup(
        mirror_dir=a.mirror_dir, output_fn=a.output_fn, bk_path=a.bk_path, lfns=a.lfns,
        lfns_fn=a.lfns_fn, production_id=a.production_id, batch=a.batch))

    args = parser.parse_args()
    args.func(args)


def lookup(mirror_dir=None, output_fn=None, batch=None,
           bk_path=None, lfns=None, lfns_fn=None, production_id=None):
    if sum(map(bool, [batch, bk_path, lfns, lfns_fn, production_id])) != 1:
        raise ValueError('One and only one of "bk_path", "lfns", "lfns_fn", '
                         '"production_id" and "batch" should be passed')

    if batch is not None:
        if output_fn:
            raise NotImplementedError('output_fn cannot be used with batch')

        options = {
            'BKQUERY': 'bk_path',
            'LFN': 'lfns',
            'LFNs': 'lfns_fn',
            'PRODID': 'production_id',
        }

        with open(batch, 'rt') as fp:
            jobs = {k: v if isinstance(v, list) else [v]
                    for k, v in json.load(fp).items()}

        for directory, commands in jobs.items():
            for command in commands:
                directory = join(mirror_dir, directory)
                match = re.match(r'^(BKQUERY|LFN|LFNs|PRODID):(.*)$', command)
                if match is None:
                    raise ValueError('Invalid command "' + command + '"')
                lookup(directory, **{options[match.group(1)]: match.group(2)})

        return

    if bk_path is not None:
        if not isinstance(bk_path, list):
            bk_path = [bk_path]
        files = lookup_files_from_query(bk_path)

    if lfns_fn is not None:
        with open(lfns_fn, 'rt') as fp:
            files = {lfn.strip(): {} for lfn in fp.read().split('\n')}

    if lfns is not None:
        if not isinstance(lfns, list):
            lfns = [lfns]
        files = {lfn: {} for lfn in lfns}

    if production_id is not None:
        if not isinstance(production_id, list):
            production_id = [production_id]
        raise NotImplementedError()

    loookup_replicas(files)
    if output_fn:
        dump(files, output_fn)

    if mirror_dir:
        mirror_files(files, mirror_dir)


if __name__ == '__main__':
    parse_args()
