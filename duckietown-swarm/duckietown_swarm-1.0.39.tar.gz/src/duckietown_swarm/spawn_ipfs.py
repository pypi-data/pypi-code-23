from duckietown_swarm.process_manager import ProcessManager
import json
from multiprocessing import Process
import os

from system_cmd.meat import system_cmd_result

import subprocess32 as subprocess


#import sys
#if os.name == 'posix' and sys.version_info[0] < 3:
#    import subprocess32 as subprocess
#else:
#    import subprocess
def initialize_ipfs(repo_dir):
    env = os.environ.copy()
    env['IPFS_PATH'] = repo_dir

    if not os.path.exists(repo_dir):
        cmd = ['ipfs', 'init']
        system_cmd_result(cwd='.', cmd=cmd, env=env)


def _run_ipfs(repo_dir):

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
        cmd = ['ipfs', 'config', name, '--json', json.dumps(data)]
        env = os.environ.copy()
        env['IPFS_PATH'] = repo_dir
        system_cmd_result(cwd='.', cmd=cmd, env=env)

    set_config('Addresses.API', '/ip4/127.0.0.1/tcp/%s' % port_api)
    set_config('Addresses.Gateway', '/ip4/0.0.0.0/tcp/%s' % port_gw)
    set_config('Addresses.Swarm', ["/ip4/0.0.0.0/tcp/%s" % port_swarm])
    set_config('Swarm.EnableRelayHop', False)
    set_config('Swarm.ConnMgr.LowWater', 10)
    set_config('Swarm.ConnMgr.HighWater', 20)

#
    env = os.environ.copy()
    env['IPFS_PATH'] = repo_dir
#    cmd = ['ipfs', 'bootstrap', 'add']
#    system_cmd_result(cwd='.', cmd=cmd, env=env)

    stdout = open(os.path.join(repo_dir, 'stdout.log'), 'w')
    stderr = open(os.path.join(repo_dir, 'stderr.log'), 'w')
    print('Starting daemon')
    cmd = [
        'ipfs', 'daemon',
        '--enable-pubsub-experiment',
        '--routing=dhtclient',
    ]
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
            raise Exception(ret)
    finally:
        stderr.write('Finished.')
        stdout.write('Finished.')
        stderr.close()
        stdout.close()
        print('Finished')


def run_ipfs(repo_dir):
    args = (repo_dir,)
    pm = ProcessManager(_run_ipfs,
                                args, 'run_ipfs',
                                restart=True)
    pm.start()

