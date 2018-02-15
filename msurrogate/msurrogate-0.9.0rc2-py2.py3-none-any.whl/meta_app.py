"""
An msurrogate model server. Start this code to connect from other applications
"""
from __future__ import division, print_function, unicode_literals
import argparse
import socket
import Pyro4
import collections
import sys
import json
import uuid

from .meta_daemon import MetaDaemon

if sys.version_info > (3, 0):
    pass
else:
    input = raw_input


class SurrogateApp(object):

    def __init__(
        self,
        argparser = None,
    ):

        if argparser is None:
            argparser = argparse.ArgumentParser(
                description = __doc__
            )
        self.argparser = argparser

        self.forced = set()
        self.defaults = {
            'public'         :         False,
            'host'           :         None,
            'pubhost'        :         None,
            'pubport'        :         None,
            'port'           :         None,
            'cookiefile'     :         None,
            'secret'         :         None,
            'workers'        :         4,
            'multithread'    :         True,
            #non-config options
            'allow-dill'     :         False,
            'allow-pickle'   :         True,
            'workspace-auto' :         True,
            'multithreaded-auto-off' : False,
            'hide-secret' :            True,
            'serializer-preferred' :   None,
        }

        self.args        = None
        self.daemon      = None
        self.meta_daemon = None

    def option(self, name, value, force = False):
        if force:
            self.forced.add(name)
        else:
            try:
                self.forced.remove(name)
            except KeyError:
                pass
        self.defaults[name] = value
        return

    def parse_args(self, args = None):
        """
        Setup the remainder of the argparser and then parse the arguments
        """

        #public
        #use this if it should ever bind off of localhost (must be explicit)
        if 'public' not in self.forced:
            self.argparser.add_argument(
                '--public', dest = 'public', default = self.defaults['public'],
                action = 'store_true',
                help = 'Allow binding on exposed interfaces (required for host/pubhost to work)'
            )

            if 'host' not in self.forced:
                #host
                #host
                self.argparser.add_argument(
                    '-n', '--host', dest = 'host', default = self.defaults['host'],
                    help = (
                        'Hostname to bind to. Defaults to localhost unless public is specified, '
                        'in which case the default is the current hostname. '
                        'May be "*" to bind all interfaces, but pubhost should also be provided'
                    ),
                )

            #pubhost
            if 'pubhost' not in self.forced:
                self.argparser.add_argument(
                    '-N', '--public-host', dest = 'pubhost', default = self.defaults['pubhost'],
                    help = (
                        'Hostname to provide for URIs '
                        'defaults to the same as host, unless host is "*" and pubhost should be provided'
                    ),
                )
            #host name through NAT

        #port
        #default (None) is a random port
        if 'port' not in self.forced:
            self.argparser.add_argument(
                '-p, --port', dest = 'port', default = self.defaults['port'],
                type = int,
                help = (
                    'port to listen on. Defaults to a random unused port'
                ),
            )

        #pubport
        #port forearded through NAT
        if 'pubport' not in self.forced:
            self.argparser.add_argument(
                '-P', '--public-port', dest = 'pubport', default = self.defaults['pubport'],
                type = int,
                help = (
                    'port to provide in URIs. Should be forwarded through a NAT.'
                ),
            )

        #secret
        #secret to use for connection start
        #if it is '-' then it will be specified through stdin
        if 'secret' not in self.forced:
            self.argparser.add_argument(
                '-S', '--secret', dest = 'secret', default = self.defaults['secret'],
                help = (
                    'Secret Phrase for slight security. Default is random. May be "-" to read from stdin. '
                    'May be "" to not use a secret'
                ),
            )

        #cookiefile
        #if it is '-' it will be output to stdout
        #if it is '' there will be NO output
        if 'cookiefile' not in self.forced:
            self.argparser.add_argument(
                '-c', '--cookie-file', dest = 'cookiefile', default = self.defaults['cookiefile'],
                help = (
                    'cookie file to write with interface URIs and connection information. '
                    'May be "-" to supply on stdout. May be "" to write no file at all.'
                ),
            )

        #multithread
        #if true, specify and use it in Pyro4
        #if false, use single threaded server
        #if None, don't specify (default is threaded), presumably the user wants to override
        def_MT = self.defaults['multithread']
        if 'multithread' not in self.forced:
            if def_MT is None:
                #don't specify, user is doing it
                pass
            elif def_MT:
                self.argparser.add_argument(
                    '-M, --no-multithread', dest = 'multithread', default = def_MT,
                    action = 'store_false',
                    help = (
                        'Disable multithreaded operation. Workers is effectively one. Use if OS is running out of threads during connection.'
                    ),
                )
            else:
                self.argparser.add_argument(
                    '-m, --with-multithread', dest = 'multithread', default = def_MT,
                    action = 'store_true',
                    help = (
                        'Enable multithreaded operation. Workers is then used.'
                    ),
                )

        if 'workers' not in self.forced:
            #workers
            #number of workers to bound with the semaphore, of multithread is forced false, it wont be asked
            self.argparser.add_argument(
                '-W', '--workers', dest = 'workers', default = None,
                help = (
                    'Workers limit for computation. Limits the number of simultaneously running threads. Each connection still gets a thread.'
                ),
            )

        self.args = self.argparser.parse_args(args)

        for k, v in self.defaults.items():
            if k not in self.args:
                self.args.__dict__[k] = v

        #now check!
        self.multithread = self.args.multithread
        if self.args.multithread is not None:
            if self.args.multithread:
                if self.args.workers is None:
                    self.workers = self.defaults['workers']
                else:
                    self.workers = self.args.workers
                if self.workers < 1:
                    raise RuntimeError("Number of Workers must be greater than 0")
                if self.workers == 1 and self.defaults['multithreaded-auto-off']:
                    self.multithread = False
            else:
                if self.args.workers is not None:
                    raise RuntimeError("Cannot Specify Workers if not running multithreaded")
                self.workers = None

        self.public  = self.args.public
        self.host    = self.args.host
        self.pubhost = self.args.pubhost
        self.port    = self.args.port
        if self.port is None:
            self.port = 0
        self.pubport = self.args.pubport

        if not self.public:
            if self.args.host is not None:
                raise RuntimeError("Cannot Specify Host if not running public")
            self.host = 'localhost'
        else:
            if self.host is None:
                self.host = socket.gethostname()

        self.secret = self.args.secret
        self.cookiefile = self.args.cookiefile
        if self.cookiefile is None:
            raise RuntimeError("Must Specify a cookiefile to output")

        if self.multithread is None:
            pass
        elif self.multithread:
            Pyro4.config.SERVERTYPE = 'thread'
        else:
            Pyro4.config.SERVERTYPE = 'multiplex'

        if self.secret == '-':
            self.secret = input()
            if self.defaults['hide-secret']:
                self.hide_secret = True
            else:
                self.hide_secret = False
        elif self.secret is None:
            self.secret = str(uuid.uuid4())
            self.hide_secret = False
        else:
            self.hide_secret = False

        if self.secret is not '':
            Pyro4.Daemon._pyroHmacKey = bytes(self.secret)
            Pyro4.Proxy._pyroHmacKey = bytes(self.secret)

        Pyro4.config.SERIALIZERS_ACCEPTED = set(Pyro4.config.SERIALIZERS_ACCEPTED)
        if self.defaults['allow-dill']:
            Pyro4.config.SERIALIZERS_ACCEPTED.add('dill')
        if self.defaults['allow-pickle']:
            Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        return

    def daemon_setup(self, daemon = None):
        if self.args is None:
            self.parse_args()

        if self.daemon is None:
            if daemon is None:
                self.daemon = Pyro4.Daemon(
                    host    = self.host,
                    port    = self.port,
                    nathost = self.pubhost,
                    natport = self.pubport,
                )
            else:
                self.daemon = daemon
        return

    def meta_daemon_setup(self, meta_daemon = None):
        if self.meta_daemon is None:
            if self.daemon is None:
                self.daemon_setup()

            if meta_daemon is None:
                self.meta_daemon = MetaDaemon(
                    daemon = self.daemon,
                    workers_N = self.workers,
                )
            else:
                self.meta_daemon = meta_daemon

        if self.defaults['workspace-auto']:
            self.meta_daemon.register(self.meta_daemon.workspace_dict)
            self.meta_daemon.register(self.meta_daemon.workspace_reset)
            self.meta_daemon.register(self.meta_daemon.workspace_counts)
            self.meta_daemon.register(self.meta_daemon.workspace_gc)
            self.meta_daemon.register(self.meta_daemon.workspace_close)

        return self.meta_daemon

    def cookie_dict(self):
        d = dict(
            workspace = self.meta_daemon.workspace_dict(),
            host      = self.host,
        )
        if not self.hide_secret:
            d['secret'] = self.secret
        serializer_pref = self.defaults['serializer-preferred']
        if serializer_pref is not None:
            d['serializer-preferred'] = serializer_pref
        return d

    def cookie_write(self):
        if self.meta_daemon is None:
            self.meta_daemon_setup()

        if self.cookiefile == '':
            #no cookie
            pass
        elif self.cookiefile == '-':
            #guarantee a newline before COOKIE_START and AFTER COOKIE_END
            print('')
            print('COOKIE_START')
            json.dump(
                self.cookie_dict(), sys.stdout,
                indent = 4,
                sort_keys = True,
            )
            print()
            print('COOKIE_END')
            sys.stdout.flush()
        else:
            with open(self.cookiefile, 'w') as F:
                json.dump(
                    self.cookie_dict(), F,
                    indent = 4,
                    sort_keys = True,
                )

    def run_loop(self):
        if self.meta_daemon is None:
            self.meta_daemon_setup()

        self.cookie_write()
        self.meta_daemon.daemon.requestLoop()
        return


def cookie_setup(cookie_dict):
    if not isinstance(cookie_dict, collections.Mapping):
        #then it must be a string
        cookie_dict = json.loads(cookie_dict)

    secret = cookie_dict.get('secret', '')

    if secret is not None and secret != '':
        Pyro4.Daemon._pyroHmacKey = bytes(secret)
        Pyro4.Proxy._pyroHmacKey  = bytes(secret)

    serializer = cookie_dict.get('serializer-preferred', None)

    if serializer is not None:
        Pyro4.config.SERIALIZER = serializer

    sys.excepthook = Pyro4.util.excepthook
    return cookie_dict['workspace']






