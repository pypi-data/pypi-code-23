import argparse
import os
import sys

from .config import read_config, get_repos
from .vcs import clone, pull, push, set_remote, sync


def _add_arg_repo(parser):
    parser.add_argument(
        '-r', '--repo', help='repository to act on, default: "all"',
        default='all')
    return parser


def _add_arg_branch(parser):
    parser.add_argument(
        '-b', '--branch', help='branch to act on, default: "default"',
        default='default')
    return parser


def get_parser():
    parser = argparse.ArgumentParser(
        prog='fluidmirror',
        description=(
            'works on a specific / all configured repositories (default)')
    )
    parser.add_argument(
        '-c', '--cfg', help='config file', default='mirror.cfg')
    subparsers = parser.add_subparsers(help='sub-command')

    parser_list = subparsers.add_parser(
        'list', help='list configuration')
    parser_list.set_defaults(func=_list)

    parser_clone = subparsers.add_parser(
        'clone', help='hg clone')
    parser_clone.set_defaults(func=_clone_all)

    parser_setr = subparsers.add_parser(
        'set-remote',
        help=('set remote (push) path in hgrc'))
    parser_setr.set_defaults(func=_setr_all)

    parser_pull = subparsers.add_parser(
        'pull', help='hg pull -u')
    parser_pull.set_defaults(func=_pull_all)

    parser_push = subparsers.add_parser(
        'push', help='hg push')
    parser_push.set_defaults(func=_push_all)

    parser_sync = subparsers.add_parser(
        'sync', help='sync: pull and push ')
    parser_sync.set_defaults(func=_sync_all)

    for subparser in [parser_list, parser_clone, parser_setr, parser_pull,
                      parser_push, parser_sync]:
        _add_arg_repo(subparser)

    for subparser in [parser_push, parser_sync]:
        _add_arg_branch(subparser)

    return parser


def _list(args):
    read_config(args.cfg, output=True)


def _config(args):
    config = read_config(args.cfg)
    dirname = os.path.dirname(args.cfg)
    if dirname == '':
        dirname = os.curdir

    os.chdir(dirname)
    if config['defaults']['ssh'] != '':
        hgopts = ' -e "{}" '.format(
            os.path.expandvars(config['defaults']['ssh']))
    else:
        hgopts = ''

    return config, hgopts


def _all(func, args, key='pull'):
    config, hgopts = _config(args)
    if hasattr(args, 'branch'):
        kwargs = {'branch': args.branch}
    else:
        kwargs = {}

    if args.repo == 'all':
        for repo in get_repos(config.sections()):
            func(config['repo:' + repo][key], repo, hgopts=hgopts, **kwargs)
    else:
        repo = args.repo
        func(config['repo:' + repo][key], repo, hgopts=hgopts, **kwargs)


_clone_all = lambda args: _all(clone, args)
_setr_all = lambda args: _all(set_remote, args, 'push')
_pull_all = lambda args: _all(pull, args)
_push_all = lambda args: _all(push, args, 'push')


def _sync_all(args):
    config, hgopts = _config(args)
    if args.repo == 'all':
        for repo in get_repos(config.sections()):
            sync(repo, config['repo:' + repo]['pull'],
                 config['repo:' + repo]['push'], hgopts=hgopts, branch=args.branch)
    else:
        repo = args.repo
        sync(repo, config['repo:' + repo]['pull'],
             config['repo:' + repo]['push'], hgopts=hgopts, branch=args.branch)


def main(*args):
    parser = get_parser()
    args = parser.parse_args(*args)
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
