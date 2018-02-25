from Queue import Empty
import argparse
import getpass
import random
import subprocess
import sys

from contracts import contract
from system_cmd import CmdException
import yaml

from .brain import DistributedRepoSwarm
from .dcache import Envelope, interpret_message
from .dcache_wire import create_command_message
from .dcache_wire import create_request_message, MsgPong
from .ipfs_utils import IPFSInterface
from .packaging import find_more_information
from .socket_utils import AsyncLineBasedConnection
from .utils import now_until


@contract(returns=DistributedRepoSwarm, patterns=list)
def get_snapshot(host, port, patterns):

    albc = AsyncLineBasedConnection(host, port)
    maddr_from = '/cli'

    inbound = albc.get_q_inbound()
    outbound = albc.get_q_outbound()

    msg = create_request_message(patterns, validity=now_until(105))

    e = Envelope(maddr_from=maddr_from,
                 maddr_to='/dswarm/*/brain',
                 contents=msg)

    outbound.put(e)

    dc = DistributedRepoSwarm()
    from_channel = 'stdin'
    i = 0

#    wait_since_last = 15.0
#    t_last = time.time()
    while True:
        try:
            env = inbound.get(block=True, timeout=1.0)
#            t_last = time.time()
            is_signature = 'signature' in env.contents
            if is_signature:
                sys.stderr.write('S')
            else:
                sys.stderr.write('r')
        except Empty:
            pass
#            if i > 0:
#                if time.time() - t_last > wait_since_last:
#                    break
        else:
#            print env
            msg = interpret_message(env.contents)
            if isinstance(msg, MsgPong):
                break
            dc.process(env.contents, from_channel)
        i += 1
    print('processed %s messages' % i)
    return dc


DSWARM_API_PORT = 8000


def duckietown_swarm_cli_main():

    parser = argparse.ArgumentParser(description='Ping the swarm')
    parser.add_argument('--host', type=str, help='host to use', default='localhost')
    parser.add_argument('command', type=str, help='command')
    parser.add_argument('rest', nargs=argparse.REMAINDER, help='rest')
    parsed = parser.parse_args()

    host = parsed.host
    port = DSWARM_API_PORT
    cmd = parsed.command
    args = parsed.rest

    if cmd == 'summary':
        if args:
            what = args
        else:
            what = ['*']

        dc = get_snapshot(host, port, what)
        data = dc.summary_dict()

        print(yaml.dump(data))

    elif cmd == 'report':
        what = ['/verified', '/files', '/safe']
        dc = get_snapshot(host, port, what)
        ipfsi = IPFSInterface(None)

        if args:
            find_provs = True
            provs_timeout = args.pop(0)
        else:
            find_provs = False
            provs_timeout = None

        s = create_safe_index(ipfsi, dc, find_provs, provs_timeout)
        mh = ipfsi.add(s)
        url = 'http://localhost:6080/ipfs/' + mh

        print url
    elif cmd == 'ipfs':
        ipfsi = IPFSInterface(None)
        ipfs = ipfsi.get_executable()
        cmd = [ipfs] + args
        p = subprocess.Popen(
                cmd,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                bufsize=0,
                cwd='.',
                env=ipfsi._get_env())
        p.wait()

    elif cmd == 'ssh':
        do_ssh(host, port, args)
    elif cmd == 'shell':
        do_shell(host, port, args)
    elif cmd == 'cmd':
        arg = args[0]
        parameters = {}
        send_cmd(host, arg, parameters)
    else:
        raise Exception(cmd)


def do_shell(host, port, args):
    ipfsi = IPFSInterface(None)
    hostname = args.pop(0)

    try:
        peer = resolve_name(host, port, hostname)
    except NoNameFound as e:
        print e
        return

    print('connecting to peer %s' % peer)
    try:
        ipfsi.swarm_connect("/p2p-circuit/ipfs/%s" % peer)
    except CmdException as e:
        print e
    port = random.randint(22000, 23232)

    cmd = ['ipfs', 'p2p', 'stream', 'dial', '--timeout', '60s',
           peer , 'p2p-shell', '/ip4/127.0.0.1/tcp/%d' % port]
    print(" ".join(cmd))
    res = ipfsi._cmd(cmd)
    print(res.stdout)

    cmd = ['ncat', 'localhost', str(port)]
    print(" ".join(cmd))

    p = subprocess.Popen(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                stdin=sys.stdin,
                bufsize=0,
                cwd='.')

    try:
        p.wait()

        ret = p.returncode
        print('Daemon exit: %s' % ret)
        if ret:
            raise Exception(ret)
    finally:
        print('Finished')


class NoNameFound(Exception):
    pass


def do_ssh(host, port, args):
    ipfsi = IPFSInterface(None)
    spec = args.pop(0)
    if '@' in spec:
        user = spec[:spec.index('@')]
        hostname = spec[spec.index('@') + 1:]
    else:
        user = getpass.getuser()
        hostname = spec

    try:
        peer = resolve_name(host, port, hostname)
    except NoNameFound:
        return

    print('Connecting to %r at %r' % (user, hostname))

    print('connecting to peer %s' % peer)
    try:
        ipfsi.swarm_connect("/p2p-circuit/ipfs/%s" % peer)
    except CmdException as e:
        print e
    port = random.randint(22000, 23232)

    cmd = ['ipfs', 'p2p', 'stream', 'dial', '--timeout', '60s',
           peer , 'p2p-ssh', '/ip4/127.0.0.1/tcp/%d' % port]
    print(" ".join(cmd))
    res = ipfsi._cmd(cmd)
    print(res.stdout)

    cmd = ['ssh', '-p', str(port), '-o', 'StrictHostKeyChecking=no',
           '%s@localhost' % user]
    print(" ".join(cmd))

    p = subprocess.Popen(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                stdin=sys.stdin,
                bufsize=0,
                cwd='.')

    try:
        p.wait()

        ret = p.returncode
        print('Daemon exit: %s' % ret)
        if ret:
            raise Exception(ret)
    finally:
        print('Finished')


def resolve_name(host, port, hostname):
    what = ["/pri/*/info/hostname"]
    dc = get_snapshot(host, port, what)
    data = dc.summary_dict()
    hostname2peerid = {}
    for peer, values in data['pri'].items():
        _hostname = list(values['info']['hostname'])[0]
        hostname2peerid[_hostname] = peer

    if not hostname in hostname2peerid:
        msg = ('No host %r found in %s' % (hostname, hostname2peerid))
        raise NoNameFound(msg)

    return hostname2peerid[hostname]


def send_cmd(host, name, parameters):
    albc = AsyncLineBasedConnection(host, DSWARM_API_PORT)
    maddr_from = '/cli'

    inbound = albc.get_q_inbound()
    outbound = albc.get_q_outbound()

    msg = create_command_message(name, parameters, validity=now_until(105))

    e = Envelope(maddr_from=maddr_from,
                 maddr_to='/dswarm/*/brain',
                 contents=msg)

    outbound.put(e)

    reply = inbound.get()
    print reply


def create_safe_index(ipfsi, dc, find_provs, provs_timeout):
    ''' Creates a webpage showing the safe data uploaded '''
    data = dc.summary_dict()

    print(yaml.dump(data))

    s = "<html><head></head><body>"

    verified = []

    data_files = data.get('files', set())
    data_safe = data.get('safe', set())
    data_verified = data.get('verified', set())

    all_mh = set(data_files) | set(data_safe) | set(data_verified)

    for mh in all_mh:
#        s += '\n<a href="/ipfs/%s">%s</a>' % (v, v)
        try:
            more_info = find_more_information(ipfsi, mh, find_provs=find_provs,
                                              provs_timeout=provs_timeout)
            if find_provs:
                print('%15s provided by %s' % (more_info.filename, more_info.providers_payload))
            sys.stderr.write(',')
        except Exception as e:
            print(e)
        else:
            verified.append(more_info)

#            if len(verified) > 10:
#                break
    verified = sorted(verified, key=lambda mi: mi.ctime)

    s += '''
        <style>
        .mh { font-family: monospace; }
        thead { font-weight: bold; }
        td { padding-left: 1em; }
        </style>

        <table>
        <thead><tr><td>Filename</td><td>Size</td><td>Upload by</td><td>node</td>
        <td></td>
        <td>safe</td>
        <td>verified</td>

        <td>ipfs_container</td>
        <td>ipfs_payload</td>
        <td>providers</td>

        </tr></thead>
        <tbody>
    '''
    for more_info in verified:
        d = more_info._asdict()
        d['is_safe'] = 'safe' if more_info.ipfs in data.get('safe', []) else ''
        d['is_verified'] = 'verified' if more_info.ipfs in data.get('verified', []) else ''
        d['date'] = more_info.ctime.strftime('%Y-%m-%d %H:%M')

        def shorten(mh):
            return '<a class="mh" href="/ipfs/%s">%s</a>' % (mh, mh[:4] + '...' + mh[-4:])

        def shorten_node(mh):
            return '<a class="mh" href="/ipns/%s">%s</a>' % (mh, mh[:4] + '...' + mh[-4:])

        d['upload_node_short'] = shorten_node(more_info.upload_node)
        d['ipfs_short'] = shorten(d['ipfs'])
        d['ipfs_payload_short'] = shorten(d['ipfs_payload'])

        d['providers'] = " ".join(map(shorten_node, more_info.providers_info))
        si = '''\n<tr><td><a href="/ipfs/{ipfs_payload}">{filename}</td><td>{size}</td>
        <td>{date}</td>
             <td></td><td> {upload_node_short}</td>
             <td>{is_safe}</td>
             <td>{is_verified}</td>
              <td>{ipfs_short}</td>
              <td>{ipfs_payload_short}</td>
                <td>{providers}</td>
              </tr> '''

        s += si.format(**d)
#        ipfs='QmTJ6sFnB2Pxe1SG7hkd84gkv1YcaEai2tP86mbJKAdBdz', ipfs_payload='QmZYND3nJUW7KAmFMKNjHRMPmtL3FZtqSXW9qNRNcownoG', ipfs_info='QmbWEnQoAL8hPsk2GftZAYC4kTjK7HFYp6eM4D7ULyKA5r', filename='stasera.txt', upload_host='dorothy-7.local', upload_node='QmQDCfGCaYk7Uqc27k6gfgYD13pjny6MZSFQDk8Ra651Jo', upload_user='andrea', ctime=datetime.datetime(2018, 2, 7, 20, 49, 41), size=26, providers_payload=[], providers_info=[])

    s += '</tbody></table>'
    s += '</body>'
    s += '</html>'
    return s


if __name__ == '__main__':
    duckietown_swarm_cli_main()
