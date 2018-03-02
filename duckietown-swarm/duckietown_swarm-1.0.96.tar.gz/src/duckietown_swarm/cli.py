from Queue import Empty
import argparse
from collections import OrderedDict
from duckietown_swarm import __version__
import getpass
import json
import random
import subprocess
import sys

from contracts import contract
from system_cmd import CmdException
from termcolor import colored
import yaml

from .brain import DistributedRepoSwarm
from .constants import DSwarmConstants
from .dcache import Envelope, interpret_message
from .dcache_wire import create_command_message
from .dcache_wire import create_request_message, MsgPong
from .ipfs_utils import IPFSInterface
from .irc2 import duckietown_swarm_main
from .packaging import find_more_information
from .ping import duckietown_swarm_ping_main
from .socket_utils import AsyncLineBasedConnection
from .utils import duration_compact
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


commands = OrderedDict()


def command(x):
    commands[x.__name__.replace('cmd_', '')] = x
    return x


@command
def cmd_version(parsed, args):  #@UnusedVariable
    print('%s' % __version__)


@command
def cmd_network(parsed, args):  #@UnusedVariable

    host = parsed.host
    port = DSwarmConstants.port_dswarm

    G = get_network(host, port)
    t = get_visjs(G)
    fn = 'network.html'
    with open(fn, 'w') as f:
        f.write(t)
    print('written %s' % fn)


def get_visjs(G):

    edges_all = []
    edges_direct = []
    nodes = []

    t = []

    def id_from_mh(x):
        if not x in t:
            t.append(x)
        return t.index(x)

#    print list(G.nodes_iter(data=True))
    for mh, data in G.nodes_iter(data=True):
        label = data.get('label', mh[-6:])
        nodes.append(dict(id=id_from_mh(mh), label=label))
        for n in G.neighbors(mh):
            direct = G.get_edge_data(mh, n)['direct']
            edges_all.append({'from': id_from_mh(mh), 'to': id_from_mh(n), 'dashes': not direct})
            if direct:
                edges_direct.append({'from': id_from_mh(mh), 'to': id_from_mh(n), 'dashes': not direct})

    t = template

    t = t.replace('EDGES_ALL', json.dumps(edges_all))
    t = t.replace('EDGES_DIRECT', json.dumps(edges_direct))
    t = t.replace('NODES', json.dumps(nodes))
    return t


#    gv.newLink(mh, mh2)
#    gv.newItem(mh)
template = '''
<!doctype html>
<html>
<head>
  <title>Network | Basic usage</title>

  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.js"></script>
  <link href="../../dist/vis-network.min.css" rel="stylesheet" type="text/css" />

  <style type="text/css">
    .networks {
      width: 800px;
      height: 800px;
      border: 1px solid lightgray;
    }
  </style>
</head>
<body>

<h3>All connections</h3>

<div class='networks' id="graph_all"></div>

<h3>Only direct connections</h3>
<div  class='networks' id="graph_direct"></div>

<script type="text/javascript">
  // create an array with nodes
  var nodes = new vis.DataSet(NODES);

  // create an array with edges
  var edges_all = new vis.DataSet(EDGES_ALL);
  var edges_direct = new vis.DataSet(EDGES_DIRECT);

  // create a network
  var container = document.getElementById('graph_all');
  var options = {};
  var network1 = new vis.Network(container, {nodes: nodes, edges:edges_all},options);
  var container = document.getElementById('graph_direct');
  var network2 = new vis.Network(container, {nodes: nodes, edges:edges_direct},options);

</script>


</body>
</html>'''


def get_network(host, port):
    what = ['*ipfs_peers', '/pri/*/info/hostname']
    dc = get_snapshot(host, port, what)
    return get_network_(dc)


def get_network_(dc):
    data = dc.summary_dict()
    print(yaml.dump(data))
    import networkx as nx
    G = nx.DiGraph()
    pri = data.get('pri', {})
    hosts = list(pri)
    mh2hostname = {}
    for mh in hosts:
        mh2hostname[mh] = pri[mh]['info']['hostname'][0]
        peers = [get_peer(_) for _ in pri[mh].get('ipfs_peers', [])]
#        print '%s->%s' % (mh, peers)

        G.add_node(mh, label=mh2hostname[mh])
        for direct, mh2 in peers:
            G.add_edge(mh, mh2, direct=direct)
    return G


def get_peer(con):
#    /ipfs/QmVKMTGqtgDHMSrGDQnpodnQq4C84kH2Y9v9FGwN8XPtxa/p2p-circuit/ipfs/QmYZQjusVBHq7uWWWrpcghCF1Nyfa3daD3EyfLNdcmERCR,
#      /ipfs/QmVKMTGqtgDHMSrGDQnpodnQq4C84kH2Y9v9FGwN8XPtxa/p2p-circuit/ipfs/QmdcWArNAMwW1veKYvCaSuVsm6j6zd3UWCMpH6i8ZnPuY9
    x = con.split('/')
    p = x[-1]
    assert p.startswith('Qm')
    direct = con.startswith('/ip4')
    return direct, p


@command
def cmd_summary(parsed, args):
    ''' Writes summary'''
    host = parsed.host
    port = DSwarmConstants.port_dswarm

    if args:
        what = args
    else:
        what = ['*']

    dc = get_snapshot(host, port, what)
    data = dc.summary_dict()

    print(yaml.dump(data))


@command
def cmd_online(parsed, args):
    host = parsed.host
    port = DSwarmConstants.port_dswarm

    what = ['/pri/*/version/dswarm', '/pri/*/info/hostname']

    dc = get_snapshot(host, port, what)
    data = dc.summary_dict(True, True)
    print
    h = []
    hosts = list(data['pri'])
    for mh in hosts:
        hostname = data['pri'][mh]['info']['hostname']['value']
        version = data['pri'][mh]['info']['version']['dswarm']['value']
        age = data['pri'][mh]['info']['version']['dswarm']['age']
        h.append(dict(version=version, age=age, hostname=hostname, mh=mh))

    h = sorted(h, key=lambda x: x['age'])
    for x in h:
        print('%s   %7s  %10s   %s' % (x['mh'], x['version'], duration_compact(x['age']), x['hostname'],))

#    print(yaml.dump(data))


@command
def cmd_help(parsed, args):  #@UnusedVariable
    print("Commands available:\n")
    for name, cmd in commands.items():
        use = 'dt-swarm %s ' % colored(name, attrs=['bold'])
        doc = cmd.__doc__
        if doc is not None: doc = doc.strip()
        else:
            doc = ''
        print('   %-20s %s' % (use, doc))


@command
def cmd_report(parsed, args):
    host = parsed.host
    port = DSwarmConstants.port_dswarm

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


@command
def cmd_ipfs(_parsed, args):
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


@command
def cmd_ping(_, _a):
    duckietown_swarm_ping_main()


@command
def cmd_daemon(_parsed, _args):
    duckietown_swarm_main()


def duckietown_swarm_cli_main():

    if len(sys.argv) == 1:
        cmd_help(None, [])
        return

    parser = argparse.ArgumentParser(description='Ping the swarm')
    parser.add_argument('--host', type=str, help='host to use', default='localhost')
    parser.add_argument('command', type=str, help='command')
    parser.add_argument('rest', nargs=argparse.REMAINDER, help='rest')
    parsed = parser.parse_args()

    cmd = parsed.command
    args = parsed.rest

    if not cmd in commands:
        cmd_help(parsed, args)
        return

    f = commands[cmd]
    f(parsed, args)


@command
def cmd_quit(parsed, _args):
    parameters = {}
    host = parsed.host
    send_cmd(host, 'quit', parameters)


@command
def cmd_shell(parsed, args):
    host = parsed.host
    ipfsi = IPFSInterface(None)
    hostname = args.pop(0)
    port = DSwarmConstants.port_dswarm

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


@command
def cmd_ssh(parsed, args):
    host = parsed.host
    ipfsi = IPFSInterface(None)
    spec = args.pop(0)
    if '@' in spec:
        user = spec[:spec.index('@')]
        hostname = spec[spec.index('@') + 1:]
    else:
        user = getpass.getuser()
        hostname = spec

    port = DSwarmConstants.port_dswarm
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
    port = DSwarmConstants.port_dswarm
    albc = AsyncLineBasedConnection(host, port)
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
