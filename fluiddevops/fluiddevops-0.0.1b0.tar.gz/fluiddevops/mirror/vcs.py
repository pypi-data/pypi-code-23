from __future__ import print_function

import os
import subprocess
import shlex
import configparser


def _run(cmd, output=False):
    print(cmd)
    cmd = shlex.split(cmd)
    if output:
        return subprocess.check_output(cmd).decode('utf8')
    else:
        subprocess.call(cmd)


def clone(src, dest=None, hgopts=None):
    if dest is not None and os.path.exists(dest):
        print('Skipping', dest, ': directory exists!')
        return

    _run('hg clone {} {} {}'.format(src, dest, hgopts))


def set_remote(dest, src, hgopts=None):
    path = os.path.join(src, '.hg', 'hgrc')
    config = configparser.ConfigParser()
    config.read(path)
    if 'git' in dest:
        dest = 'git+' + dest

    config.set('paths', 'github', dest)
    if not config.has_section('extensions'):
        config.add_section('extensions')

    config.set('extensions', 'hgext.bookmarks', '')
    config.set('extensions', 'hggit', '')
    with open(path, 'w') as configfile:
        config.write(configfile)

    os.chdir(src)
    subprocess.call(['hg', 'paths'])
    os.chdir('..')


def pull(src, dest, update=True, output=False, hgopts=None):
    os.chdir(dest)
    cmd = 'hg pull ' + src + hgopts
    if update:
        cmd += ' -u'

    output = _run(cmd, output)
    os.chdir('..')
    return output


def push(dest, src, hgopts=None, branch='default'):
    os.chdir(src)
    print(src)
    if 'git' in dest:
        print("Seems like a git repository, attempting to use bookmark and "
              "hg-git extenstions...")
        if branch == 'default':
            _run('hg bookmark -r default master')
        else:
            output = _run('hg branches', output=True)
            if branch in output:
                output = _run('hg bookmark -r ' + branch + ' branch-' + branch)
            else:
                print('Branch', branch, 'is closed or does not exist.')
                os.chdir('..')
                return

        _run('hg push git+' + dest + hgopts)
    else:
        _run('hg push ' + dest + hgopts + ' -b ' + branch)

    os.chdir('..')


def sync(src, pull_repo, push_repo, hgopts=None, branch='default'):
    output = pull(pull_repo, src, output=True, hgopts=hgopts)
    if all([string not in output for string in ['no changes', 'abort']]):
        push(push_repo, src, hgopts=hgopts, branch=branch)
