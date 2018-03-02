from __future__ import print_function

import sys
import os
import subprocess
import argparse
import time
import re
import json
import socket

from os import environ as env


class Dobro(object):

    # --- Constants ---

    VERSION = '0.4.0'

    PROGRAM_NAME = 'dobro'
    PROGRAM_DESCRIPTION = (
        '%s - tag-centric digitalocean droplet manager'
        % PROGRAM_NAME
    )
    NEW_MARKER = 'new'
    LOG_SEPARATOR = ': '

    SSH_DEFAULT_PORT = 22
    SSH_POLL_PERIOD = 3

    DELETE_GRACE_PERIOD = 5

    DEBUG = 'debug'
    INFO = 'info'
    WARN = ['warn', '33']
    ERROR = ['error', '31']

    PATTERN_ID = re.compile('^[1-9][0-9]*$')
    PATTERN_IP = re.compile('^^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)\
{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    PATTERN_TAG = re.compile('^[a-zA-Z_][a-zA-Z0-9_-]*$')


    def __init__(self):
        self.cli_args = None

        self.NAMESPACE = env.get('DOBRO_NAMESPACE', 'bro')
        self.SSH_PRIVATE_KEY_PATH = env.get(
            'DOBRO_SSH_PRIVATE_KEY',
            env['HOME'] + '/.ssh/id_rsa'
        )
        self.SSH_PUBLIC_KEY_PATH = env.get(
            'DOBRO_SSH_PUBLIC_KEY',
            self.SSH_PRIVATE_KEY_PATH + '.pub'
        )
        self.NEW_DROPLET_ARGS = env.get('DOBRO_NEW_DROPLET_ARGS', '--region \
lon1 --size 512mb --image ubuntu-16-04-x64').split(' ')
        self.NEW_DROPLET_TAGS = env.get('DOBRO_NEW_DROPLET_TAGS')

        self.DOCTL_EXTRA_ARGS = env.get('DOBRO_DOCTL_EXTRA_ARGS', False)

        # prevent [''] (see #10, #26 on GitHub)
        if self.DOCTL_EXTRA_ARGS:
            self.DOCTL_EXTRA_ARGS = self.DOCTL_EXTRA_ARGS.split(' ')
        else:
            self.DOCTL_EXTRA_ARGS = []
        if self.NEW_DROPLET_TAGS:
            self.NEW_DROPLET_TAGS = self.NEW_DROPLET_TAGS.split(' ')
        else:
            self.NEW_DROPLET_TAGS = []


    def cli(self, test=False):
        parser = argparse.ArgumentParser(prog=self.PROGRAM_NAME, description=self.PROGRAM_DESCRIPTION)

        parser.add_argument('-q', '--quiet',   help="suppress output", action='store_true')
        parser.add_argument('-v', '--verbose', help="verbose output", action='store_true')
        parser.add_argument('--no-hooks',      help="don't call hooks", action='store_true')
        subparsers = parser.add_subparsers(help="sub-command help")

        parser_create = subparsers.add_parser('create', help="create droplets")
        parser_create.add_argument('-n', '--name', help="optional droplet name (instead of id)")
        parser_create.add_argument('-c', '--droplet-count', type=int, default=1, help="number of droplets to create")
        parser_create.add_argument('tag', nargs='*', help="droplet tags")
        parser_create.set_defaults(func=self.cmd_create)

        parser_list = subparsers.add_parser('list', help="list droplets in namespace")
        parser_list.add_argument('-a', '--all', action='store_true', help="include droplets not in namespace")
        parser_list.set_defaults(func=self.cmd_list)

        parser_tagger = {}
        for either in [['tag', 'add'], ['untag', 'remove']]:
            parser_tagger[either[0]] = subparsers.add_parser(either[0], help=either[1] + " tags to droplets")
            parser_tagger[either[0]].add_argument('-c', '--criteria', metavar="ID|IP|TAG", nargs='+', required=True, help="droplet id, public ipv4 address or tags")
            parser_tagger[either[0]].add_argument('-t', '--tag', nargs='+', required=True, help="tags to " + either[1])
            parser_tagger[either[0]].set_defaults(func=eval('self.cmd_' + either[0]))

        parser_sshkey = subparsers.add_parser('ssh-key', help="ensure key is up-to-date on digitalocean")
        parser_sshkey.set_defaults(func=self.cmd_sshkey)

        parser_delete = subparsers.add_parser('delete', help="delete droplets")
        parser_delete.add_argument('--no-prompt', action='store_true', help="don't prompt before deletion")
        parser_delete.add_argument('criteria', metavar="ID|IP|TAG", nargs='+', help="droplet id, public ipv4 address or tags")
        parser_delete.set_defaults(func=self.cmd_delete)

        parser_version = subparsers.add_parser('version', help="print version information")
        parser_version.set_defaults(func=self.cmd_version)

        if not test:
            self.cli_args = parser.parse_args()
            self.cli_args.func()
        else:
            return parser


    # --- Helpers ---

    # Quote
    def q(self, s):
        return "'%s'" % s

    def colour(self, s, code=False):
        if code:
            return "\033[%sm%s\033[39m" % (code, s)
        return s

    def log(self, level, *args):
        #http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)

        if isinstance(level, basestring):
            level_s = level
            c = None
        else:
            level_s = level[0]
            c = level[1]

        s = self.colour('[%s - %s] %s' % (
            self.PROGRAM_NAME,
            level_s,
            self.LOG_SEPARATOR.join(map(lambda x: str(x), args))
        ), c)

        if level == self.DEBUG and self.cli_args.verbose and not self.cli_args.quiet:
            print(s)
        elif level == self.INFO and not self.cli_args.quiet:
            print(s)
        elif level == self.WARN or level == self.ERROR:
            eprint(s)

    def doctl(self, *args, **kwargs):
        def crash_out(err):
            a = list(args[0:3]) + [err]
            self.log(self.ERROR, *a)

        args_full = (
            ['doctl', 'compute'] +
            list(args) + [
            '--output', kwargs.get('output', 'json'),
            ] + self.DOCTL_EXTRA_ARGS
        )
        self.log(self.DEBUG, args_full)
        p = subprocess.Popen(
            args_full,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        all_output = p.communicate()
        stdout = all_output[0].strip()
        stderr = all_output[1].strip()

        if p.returncode != 0:
            # on erroring, doctl sometimes sends error info to stdout and usage to
            # stderr. weird.
            s = stdout or stderr
            crash_out('"%s"' % s)
            exit(p.returncode)

        try:
            j = None
            if kwargs.get('output', 'json') == 'json' and stdout != '':
                j = json.loads(stdout)
                l = list(args[0:3]) + ['success', j]
                self.log(self.DEBUG, *l)
            if j: return j
            return stdout
        except ValueError as e:
            crash_out('json decode error')
            exit(1)

    def list_entities(self, entity):
        self.log(self.DEBUG, entity, "list")
        l = self.doctl(entity, 'list')
        self.log(self.DEBUG, entity, "read", "success", str(l))
        return l

    def droplet_ip(self, droplet):
        for interface in droplet['networks']['v4']:
            if interface['type'] == 'public':
                return interface['ip_address']

    def sync_ssh_key(self):
        do_key_name = '%s-%s' % (self.PROGRAM_NAME, self.NAMESPACE)
        self.log(self.DEBUG, "ssh-key", "local read", self.SSH_PUBLIC_KEY_PATH)
        current_key = None
        with open(self.SSH_PUBLIC_KEY_PATH, 'r') as f:
            current_key = f.read()
        self.log(self.DEBUG, "ssh-key", "local read", "success", current_key)

        ssh_keys = self.list_entities('ssh-key')

        use_key = False
        for key in ssh_keys:
            if key['name'] == do_key_name:
                self.log(self.DEBUG, "ssh-key", "exists", self.q(do_key_name))
                use_key = key
                break
        if not use_key:
            self.log(self.DEBUG, "ssh-key", "not found", self.q(do_key_name))

        def push(method):
            self.log(self.INFO, "ssh-key", method, self.q(do_key_name))

            if method == 'update':
                self.doctl('ssh-key', 'delete', str(use_key['id']))

            output = self.doctl('ssh-key', 'create',
                do_key_name,
                '--public-key',
                current_key,
            )
            return output[0]['id']

        if use_key:
            if use_key['public_key'].strip() != current_key.strip():
                return push('update')
            return use_key['id']
        else:
            return push('create')

    def create_tags(self):
        all_tags = list(set(self.cli_args.tag + self.NEW_DROPLET_TAGS))

        err = False
        for tag in all_tags:
            if not self.PATTERN_TAG.match(tag):
                self.log(self.ERROR, "tag", "invalid format", self.q(tag))
                err = True
        if err:
            exit(1)

        # Filter out existing tags from cli args tags list
        existing_tags = map(lambda x: x['name'], self.list_entities('tag'))
        tags_needed = list(all_tags)
        for tag in existing_tags:
            if tag in tags_needed:
                tags_needed.remove(tag)

        # Create new tags
        if tags_needed:
            for tag in tags_needed:
                self.log(self.INFO, "tag", "create", self.q(tag))
                self.doctl('tag', 'create', tag)

    def tag_droplet(self, droplet, **kwargs):
        # doctl doesn't always set the tags array on new droplets
        if not ('tags' in droplet):
            droplet['tags'] = []
        tags = list(self.cli_args.tag)
        if kwargs.get('new', False):
            tags = list(set(tags + self.NEW_DROPLET_TAGS))
        for tag in tags:
            if tag in droplet['tags']:
                continue
            self.log(self.INFO, "droplet", "tag", '%s => %s' % (self.q(droplet['name']), self.q(tag)))
            self.doctl('droplet', 'tag',
                str(droplet['id']),
                '--tag-name',
                tag,
            )

    def untag_droplet(self, droplet, **kwargs):
        tags = list(self.cli_args.tag)
        for tag in tags:
            if not (tag in droplet['tags']):
                continue
            self.log(self.INFO, "droplet", "untag", '%s => %s' % (self.q(droplet['name']), self.q(tag)))
            self.doctl('droplet', 'untag',
                str(droplet['id']),
                '--tag-name',
                tag,
            )

    def resolve_droplets(self):
        all_droplets = self.list_entities('droplet')
        resolved_ids = set()
        tags = set()

        droplets = []
        for droplet in all_droplets:
            if droplet['name'].startswith(self.NAMESPACE + '-'):
                droplets.append(droplet)

        for criterion in self.cli_args.criteria:
            if self.PATTERN_ID.match(criterion):
                for droplet in droplets:
                    if str(droplet['id']) == criterion:
                        resolved_ids.add(droplet['id'])
                        break
            elif self.PATTERN_IP.match(criterion):
                for droplet in droplets:
                    if self.droplet_ip(droplet) == criterion:
                        resolved_ids.add(droplet['id'])
                        break
            elif self.PATTERN_TAG.match(criterion):
                tags.add(criterion)
            else:
                self.log(self.WARN, "argument", "not an id/ip/tag", self.q(criterion))

        if tags:
            for droplet in droplets:
                if set(droplet['tags']).issuperset(tags):
                    resolved_ids.add(droplet['id'])

        if not resolved_ids:
            self.log(self.INFO, 'droplet', 'none matched')
            exit(0)

        # dicts aren't hashable - so we've stored the set of droplets by id.
        # Here we retrieve the whole dicts again.
        resolved_droplets = []
        for droplet_id in resolved_ids:
            for droplet in droplets:
                if droplet['id'] == droplet_id:
                    resolved_droplets.append(droplet)
                    break

        return resolved_droplets

    def hook_path(self, h):
        path = '/'.join([os.environ['HOME'], '.dobro', 'hooks', h])
        if os.path.isfile(path):
            return path
        return False

    def hook(self, h):
        if self.cli_args.no_hooks:
            return
        path = self.hook_path(h)
        if path:
            self.log(self.INFO, "hook", h)
            r = subprocess.call([path])
            if r != 0:
                self.log(self.ERROR, "hook", h, "returned non-zero exit status", str(r))


    # --- Commands ---

    def cmd_create(self):
        self.hook('pre')
        key_id = self.sync_ssh_key()

        names = []
        for n in range(0, self.cli_args.droplet_count):
            if not self.cli_args.name:
                names.append('-'.join([
                    self.NAMESPACE,
                    self.NEW_MARKER,
                    time.strftime('%Y%m%d%H%M%S'),
                    str(n)
                ]))
            elif self.cli_args.droplet_count > 1:
                names.append('-'.join([
                    self.NAMESPACE,
                    self.cli_args.name,
                    str(n)
                ]))
            else:
                names.append('-'.join([
                    self.NAMESPACE,
                    self.cli_args.name
                ]))

        # Create droplets
        if len(names) > 1:
            self.log(self.INFO, "droplet", "create", "['%s']" % "', '".join(names))
        else:
            self.log(self.INFO, "droplet", "create", self.q(names[0]))
        params = ['droplet', 'create',
            ] + names + [
            '--wait',
            '--ssh-keys',
            str(key_id),
            ] + self.NEW_DROPLET_ARGS
        droplets = self.doctl(*params)

        for droplet in droplets:
            # Wait for droplet SSH listen
            # http://stackoverflow.com/questions/30615277/make-client-socket-wait-for-server-socket-with-python
            connected = False
            self.log(self.INFO, "droplet", "wait for ssh", self.q(droplet['name']))
            while not connected:
                try:
                    droplet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    droplet_socket.connect((self.droplet_ip(droplet), self.SSH_DEFAULT_PORT))
                    connected = True
                    droplet_socket.close()
                except socket.error as e:
                    time.sleep(self.SSH_POLL_PERIOD)

            # if no name specified:
            if not self.cli_args.name:
                # Rename droplets using IDs
                new_name = '%s-%s' % (self.NAMESPACE, droplet['id'])

                self.log(self.INFO, "droplet", "rename", "%s => %s" % (self.q(droplet['name']), self.q(new_name)))
                self.doctl('droplet-action', 'rename',
                    str(droplet['id']),
                    '--droplet-name',
                    new_name,
                    '--wait',
                )

                # Change droplet's internal hostname via SSH
                subprocess.check_output(['ssh', '-t',
                    '-i', self.SSH_PRIVATE_KEY_PATH,
                    '-oStrictHostKeyChecking=no',
                    '-oIdentitiesOnly=yes',
                    'root@' + self.droplet_ip(droplet),
                    '\
                    hostname %s && \
                    echo %s > /etc/hostname && \
                    sed -i -e \'s/^127\.0\.1\.1.*$/127.0.1.1 %s/g\' /etc/hosts' % (
                        self.q(new_name),
                        self.q(new_name),
                        new_name,
                    )
                ])

                # Now completely renamed server-side
                droplet['name'] = new_name

            else:
                # just check we can log in, thereby getting host key into known_hosts
                self.log(self.INFO, "droplet", "check ssh", self.q(droplet['name']))
                subprocess.check_output(['ssh', '-t',
                    'root@' + self.droplet_ip(droplet),
                    '-oStrictHostKeyChecking=no',
                    'echo waddup g'
                ])

        self.create_tags()

        for droplet in droplets:
            self.tag_droplet(droplet, new=True)

        self.hook('post')

        for droplet in droplets:
            self.log(self.INFO, "droplet", "ip",
                '%s => %s' % (self.q(droplet['name']), self.q(self.droplet_ip(droplet)))
            )

    def cmd_list(self):
        output = self.doctl('droplet', 'list', output='text')
        lines = output.splitlines()

        def print_if_ns(s):
            if not self.cli_args.all:
                print(s)

        print_if_ns(lines[0])

        not_namespaced = 0
        for line in lines[1:]:
            if self.NAMESPACE + '-' in line:
                print_if_ns(line)
            else:
                not_namespaced += 1

        if self.cli_args.all:
            print(output)

        if not_namespaced > 0:
            self.log(self.INFO, "droplet", "amount not in namespace", str(not_namespaced))


    def cmd_tag(self):
        self.hook('pre')
        self.create_tags()
        for droplet in self.resolve_droplets():
            self.tag_droplet(droplet)
        self.hook('post')

    def cmd_untag(self):
        self.hook('pre')
        for droplet in self.resolve_droplets():
            self.untag_droplet(droplet)
        self.hook('post')

    def cmd_sshkey(self):
        self.sync_ssh_key()

    def cmd_delete(self):
        self.hook('pre')

        droplets = self.resolve_droplets()
        if not self.cli_args.no_prompt:
            for droplet in droplets:
                self.log(self.INFO, "droplet", "to delete", "%s => %s" % (
                    self.q(droplet['name']),
                    "['%s']" % "', '".join(droplet['tags'])
                ))
            self.log(self.INFO, "droplet", "delete", "confirmation")
            choice = raw_input(self.colour("are you sure? [y/N] ", self.WARN[1]))
            if choice.lower() != "y" and choice.lower() != "yes":
                self.log(self.ERROR, "abort")
                exit(1)

        for droplet in droplets:
            # note output=text - 'delete' doctl command won't spit out json
            self.log(self.INFO, "droplet", "delete", self.q(droplet['name']))
            self.doctl('droplet', 'delete', str(droplet['id']), '--force', output='text')

        if self.hook_path('post'):
            self.log(self.INFO, "hook", "post", "grace period")
            time.sleep(self.DELETE_GRACE_PERIOD)
        self.hook('post')


    def cmd_version(self):
        print(self.VERSION)
