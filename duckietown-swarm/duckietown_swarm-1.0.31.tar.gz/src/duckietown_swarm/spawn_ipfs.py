import json
from multiprocessing import Process
import os
import subprocess
import sys

from system_cmd.meat import system_cmd_result


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
    set_config('Swarm.EnableRelayHop', True)
    set_config('Swarm.ConnMgr.LowWater', 10)
    set_config('Swarm.ConnMgr.HighWater', 20)

#
    env = os.environ.copy()
    env['IPFS_PATH'] = repo_dir
    cmd = ['ipfs', 'daemon', '--enable-pubsub-experiment']
#    system_cmd_result(cwd='.', cmd=cmd, env=env)
    p = subprocess.Popen(
                cmd,
#                stdin=subprocess.PIPE,
                stdout=sys.stdout,
                stderr=sys.stderr,
                bufsize=0,
                cwd='.',
                env=env)
#    p.stdin.close()
    try:
        p.wait()
        ret = p.returncode
        raise Exception(ret)
    finally:
        print('KILL the daemon')


def run_ipfs(repo_dir):

    args = (repo_dir,)
    p = Process(target=_run_ipfs, args=args)
    p.daemon = True
    p.start()

