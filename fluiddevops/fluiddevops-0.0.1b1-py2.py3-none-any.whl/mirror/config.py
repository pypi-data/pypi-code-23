from __future__ import print_function

import configparser
import sys
from os.path import join, exists


def get_repos(sections):
    return [r.split(':')[1] for r in sections if r.startswith('repo')]


def read_config(path, output=False):
    config = configparser.ConfigParser()
    if not exists(path):
        raise OSError(path + ' not found')

    config.read(path)

    pull_base = config['defaults']['pull_base']
    push_base = config['defaults']['push_base']
    repos = get_repos(config.sections())

    for repo in repos:
        if output:
            print('\nrepo:', repo)

        key = 'repo:' + repo
        pull = config[key]['pull']
        if pull == '':
            pull = join(pull_base, repo)
            config.set(key, 'pull', pull)

        push = config['repo:' + repo]['push']
        if push == '':
            push = join(push_base, repo)
            config.set(key, 'push', push)

        if output:
            print('pull:', pull)
            print('push:', push)

    return config


if __name__ == '__main__':
    read_config(sys.argv[1])
