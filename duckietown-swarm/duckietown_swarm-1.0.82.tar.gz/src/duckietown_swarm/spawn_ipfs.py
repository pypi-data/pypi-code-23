from duckietown_swarm.utils import download_url_to_file, get_sha256_for_file_hex
import json
import os
import platform

from contracts.utils import indent
from system_cmd import system_cmd_result

import subprocess32 as subprocess

from .process_manager import ProcessManager


def check_ipfs_executable(repo_dir):
    ipfs = get_ipfs_executable(repo_dir)
    cmd = [ipfs, '--version']
    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True)
    version = res.stdout
    version = version.replace('ipfs', '')
    version = version.replace('version', '')
    version = version.strip()
    print('Detected version %r at %s' % (version, ipfs))
    return version


def get_ipfs_executable(dirname):
    files = {
        'ipfs-0.4.14-dev-armv7l-Linux':
        {
            'mh': 'QmbCLdbcdDYo6KeVnwg6EngqPrm7UVXgJhyaGCPiw1et2f',
            'sha256_hex': '5c185d6d876dc63758a045c2bcd8a924c1050d2eb3d20e328b23ecf147a6e9ba',
        },
        'ipfs-0.4.14-dev-x86_64-Linux':
        {
        'sha256_hex': '7c6eda655b01d09ad5dde69afd4d13ba49953c544f1286831cb96688063422db',
        'mh': 'QmNQtAkXfRchLNt3FuCw3p2kULBEbaofY4WT3HTQMmnbJf',
        },
        'ipfs-0.4.13-x86_64-Darwin':
        {
        'sha256_hex': 'eb711715ade1deed4508bed61ec63e62ea4fe13072d0399ff243f6e01bbe9821',
        'mh': 'QmcGM8LMNAPWEcJtyan6JovQJHBMs5LDo6Lnza7nwNbJjo',
        }

    }
    choices = {
        ('armv7l', 'Linux'): 'ipfs-0.4.14-dev-armv7l-Linux',
        ('x86_64', 'Linux'): 'ipfs-0.4.14-dev-x86_64-Linux',
        ('x86_64', 'Darwin'): 'ipfs-0.4.13-x86_64-Darwin',
    }
    machine = platform.machine()
    system = platform.system()
    key = (machine, system)
    if not key in choices:
        msg = 'Could not find choice for %s in %s' % (key, choices)
        raise Exception(msg)

    filename = choices[key]
    mh = files[filename]['mh']
    sha256_hex = files[filename]['sha256_hex']

    fn = os.path.join(dirname, filename)
    if not os.path.exists(fn):
        print('Could not find %s' % fn)
        url = 'https://gateway.ipfs.io/ipfs/%s' % mh
        download_url_to_file(url, fn)

    os.chmod(fn, 0744)

    sha256_hex_found = get_sha256_for_file_hex(fn)
    if sha256_hex != sha256_hex_found:
        msg = 'Found corrupted file. \nFound hash: %s \ninstead of %s' % (sha256_hex, sha256_hex_found)
        msg += '\n\nDelete corrupted file %s' % fn
        raise Exception(msg)

    return fn


def initialize_ipfs(repo_dir):
    env = os.environ.copy()
    env['IPFS_PATH'] = repo_dir

    check = os.path.join(repo_dir, 'keystore')
    if not os.path.exists(check):
        print('Creating repo using ipfs init')
        cmd = ['ipfs', 'init']
        d = os.path.dirname(repo_dir)
        if not os.path.exists(d):
            os.makedirs(d)

        system_cmd_result(cwd='.', cmd=cmd, env=env, raise_on_error=True)
    else:

        print('Repo exists: %s' % check)


def _run_ipfs(repo_dir, use_pubsub):

#    Addresses": {
#    "API": "/ip4/127.0.0.1/tcp/5001",
#    "Announce": [],
#    "Gateway": "/ip4/127.0.0.1/tcp/8080",
#    "NoAnnounce": [],
#    "Swarm": [
#      "/ip4/0.0.0.0/tcp/4001",
#      "/ip6/::/tcp/4001"
#    ]
#  },

    base = 6000
    port_api = base + 1
    port_gw = base + 80
    port_swarm = base + 2

    def set_config(name, data):
        filename = os.path.join(repo_dir, 'config')
        with open(filename) as f:
#            contents = f.read()
            config = json.load(f)

        names = name.split('.')

        def set_config(c, name, data):
            one, rest = name[0], name[1:]
            if not one in c:
                msg = 'Could not find config %r in %s' % (one, c)
                raise KeyError(msg)
            if not rest:
                c[one] = data
            else:
                set_config(c[one], rest, data)

        set_config(config, names, data)

        with open(filename, 'w') as f:
            f.write(json.dumps(config))

#        cmd = ['ipfs', 'config', name, '--json', json.dumps(data)]
#        env = os.environ.copy()
#        env['IPFS_PATH'] = repo_dir
#        system_cmd_result(cwd='.', cmd=cmd, env=env, raise_on_error=True)
#        print('Set %s = %s' % (name, data))

    set_config('Addresses.API', '/ip4/127.0.0.1/tcp/%s' % port_api)
    set_config('Addresses.Gateway', '/ip4/0.0.0.0/tcp/%s' % port_gw)
    set_config('Addresses.Swarm', ["/ip4/0.0.0.0/tcp/%s" % port_swarm])
    set_config('Swarm.EnableRelayHop', True)
    set_config('Experimental.Libp2pStreamMounting', True)
    set_config('Swarm.ConnMgr.LowWater', 10)
    set_config('Swarm.ConnMgr.HighWater', 20)

    swarm_key = \
'''/key/swarm/psk/1.0.0/
/base16/
377f1ab022c885ab554482599939b559791442c699c24d8dcf086ab294b8f735'''

#
    env = os.environ.copy()
    env['IPFS_PATH'] = repo_dir

    swarm_key_fn = os.path.join(repo_dir, 'swarm.key')
    with open(swarm_key_fn, 'w') as f:
        f.write(swarm_key)
#    cmd = ['ipfs', 'bootstrap', 'add']
#    system_cmd_result(cwd='.', cmd=cmd, env=env)

    logdir = os.path.join(repo_dir, 'logs')
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    stderr_file = os.path.join(logdir, 'stderr.log')
    stdout = open(os.path.join(logdir, 'stdout.log'), 'w')
    stderr = open(stderr_file, 'w')
    print('Starting daemon')
    ipfs = get_ipfs_executable(repo_dir)
    cmd = [ipfs, 'daemon']

    if use_pubsub:
        cmd.append('--enable-pubsub-experiment')

    cmd.append('--routing=dhtclient')

    p = subprocess.Popen(
                cmd,
                stdout=stdout,
                stderr=stderr,
                bufsize=0,
                cwd='.',
                env=env)

    try:
        p.wait()

        ret = p.returncode
        print('Daemon exit: %s' % ret)
        if ret:
            stderr.close()
            stdout.close()
            out = open(stderr_file).read()
            msg = "Exited with: \n\n " + indent(out, '>  ')
            raise Exception(msg)
    finally:
#        stderr.write('Finished.')
#        stdout.write('Finished.')
        stderr.close()
        stdout.close()
        print('Finished')


def run_ipfs(repo_dir, use_pubsub):
    args = (repo_dir, use_pubsub)
    pm = ProcessManager(_run_ipfs,
                                args, 'run_ipfs',
                                restart=True)
    pm.start()

