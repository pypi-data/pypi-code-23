#! /usr/bin/env python
from collections import OrderedDict, namedtuple
from datetime import datetime
from duckietown_swarm import __version__
import getpass
import json
from multiprocessing import Process, Queue
import os
import random
import shutil
import socket
import subprocess
import sys
from tempfile import mkdtemp
import time

from conf_tools import locate_files
from conf_tools.utils import indent
from contracts import contract
import irc.bot  #@UnresolvedImport
from system_cmd import CmdException, system_cmd_result

from .ipfs_utils import IPFSInterface, InvalidHash
from .utils import memoize_simple, yaml_dump_omaps, yaml_load_omaps


def pinner(i):
    from duckietown_swarm.summary import get_at_least_one
    ## Read from the queue
    ipfsi = IPFSInterface()
    done = set()
    while True:
        msgs = get_at_least_one(Queues.pinner_queue, 10)
        for msg in msgs:
            msg = Queues.pinner_queue.get()

            # if msg == 'exit': break
            if msg in done:
                print('Pinner received %s twice' % msg)
                continue
            done.add(msg)

            try:
                more_info = find_more_information(ipfsi, msg, find_provs=True)
                # print more_info
            except InvalidHash as _e:
                advertise_invalid(msg, "Hash not found")
                continue
            except UnexpectedFormat as _e:
                print('Could not find more information for %s' % msg)
                advertise_invalid(msg, "Format not respected")
                continue

            print('Pinner %d %s: pinning' % (i, msg))

            cmd = ['ipfs', 'pin', 'add', '-r', '--timeout', '30s', msg]
            res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False)
            if res.ret != 0:
                print('Pinner %d %s: could not pin file' % (i, msg))
            else:
                print('Pinner %d %s: OK' % (i, msg))


adversised_invalid = set()


def advertise_invalid(ipfs_hash, comment=""):
    if ipfs_hash in adversised_invalid:
        return
    adversised_invalid.add(ipfs_hash)
    msg = {'mtype': 'advertise-invalid',
           'details': {'bucket': 'files', 'ipfs': ipfs_hash},
           'comment': comment}

    # Queues.incoming.put(msg, block=False)
    for q in Queues.outgoing + [Queues.incoming]:
        q.put(msg, block=False)


def directory_watcher(watch_dir):
    seen = {}
    tmpdir = mkdtemp(prefix='swarm')

    def look_for_files(d, pattern='*'):
        if not os.path.exists(d):
            msg = 'Logs directory does not exist: %s' % d
            raise ValueError(msg)

        filenames = locate_files(d, pattern)
        for f in filenames:
            if 'cache' in f:
                continue

            if not f in seen:

                try:
                    hashed = _add_file(f)
                except Exception as e:
                    print('error adding %s:\n%s' % (f, e))
                    continue

                print('found local %s %s' % (hashed, f))

                msg = {'mtype': 'advertise',
                       'details': {'bucket': 'files',
                                  'ipfs': hashed,
                                  'comment': "just found"}}

                Queues.incoming.put(msg, block=False)
#                for q in Queues.outgoing + [Queues.incoming]:
#                    q.put(msg, block=False)

    def _add_file(filename):
        d = setup_dir_for_file(tmpdir, filename)
        try:
            hashed = add_ipfs_dir(d)
            seen[filename] = hashed
            return hashed
        except CmdException as e:
            raise Exception(str(e))

    while True:
        look_for_files(watch_dir)
        time.sleep(15)


def pubsub_reader_process():
    cmd = ['ipfs', 'pubsub', 'sub', '--discover', 'duckiebots']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        # print('received pubsub: ' + line)
        try:
            j = json.loads(line)
            Queues.incoming.put(j, block=False)
        except ValueError as e:
            msg = 'Could not decode JSON: %s\n%r' % (e, line)
            print(msg)


def pubsub_writer_process():
    while True:
        msg = Queues.outgoing_pub.get()
        j = json.dumps(msg) + '\n'
        cmd = ['ipfs', 'pubsub', 'pub', 'duckiebots', j]
        system_cmd_result('.', cmd, raise_on_error=False)


def pubsub_friendship():
    ## Read from the queue
    ID = get_ipfs_id()

    # signal that we are here
    cmd = ['ipfs', 'block', 'put']
    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True, display_stdout=False, display_stderr=False,
                      write_stdin='duckiebots\n')
    token = res.stdout.strip()

    found = set()
    while True:
        # find other duckiebots
        cmd = ['ipfs', 'dht', 'findprovs', '--timeout', "30s", token]
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False, display_stdout=False, display_stderr=False)
        hosts = res.stdout.strip().split()
        # print('Found %s Duckiebots in the hidden botnet.' % len(hosts))
        for h in hosts:
            # do not connect to self
            if h == ID: continue
            if h in found:
                continue
            found.add(h)
            cmd = ['ipfs', 'swarm', 'connect', '--timeout', '30s', '/p2p-circuit/ipfs/' + h]
            _ = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False,
                                  display_stdout=False, display_stderr=False)
            ok = _.ret == 0
            print('Connecting to new friend %s: ' % h + ("OK" if ok else "(not possible)"))
        time.sleep(30)


class SwarmBot(irc.bot.SingleServerIRCBot):

    def __init__(self, incoming, channel, nickname):
        servers = [
                ('frankfurt.co-design.science', 6667),
#                ('irc.freenode.net', 6667),
#                ('192.168.134.1', 6667),
        ]

        irc.bot.SingleServerIRCBot.__init__(self, servers, nickname, nickname)
        self.target = channel
        self.incoming = incoming

        self.seen = {}
        self.tmpdir = mkdtemp(prefix='swarm')

        self.admitted = False
        self.disconnected = False
        self.last_broadcast = 0

        self.lateness = random.uniform(0, 10)
        self.nusers = 10

    def on_pubmsg(self, c, e):
        self._handle(c, e)

    def _handle(self, _c, e):
        s = e.arguments[0]

#        print('recv: ' + s)

        try:
            j = json.loads(s)
        except ValueError:
            return

        self.incoming.put(j)

    def on_privmsg(self, c, e):
        self._handle(c, e)

    def on_welcome(self, connection, _event):
#        print('welcome message from %s: \n%s' % (connection.server, " ".join(event.arguments)))
        connection.join(self.target)
        print('Connected to %s on IRC server %s.' % (self.target, connection.server))
        self.admitted = True

    def on_join(self, _c, _e):
        users = self.channels[self.target].users()
        self.nusers = len(users)
#        print('current users: %s' % users)

    def on_disconnect(self, _c, event):
        print('Disconnected', event.__dict__)
        self.disconnected = True

    @contract(d=dict)
    def send_message(self, d):
        json_string = json.dumps(d)
        self.connection.privmsg(self.target, json_string)
        self.last_broadcast = time.time()


def setup_dir_for_file(tmpdir, filename):
    b0 = os.path.basename(filename)
    b = b0.replace('.', '_')
    d = os.path.join(tmpdir, b)
    if not os.path.exists(d):
        os.mkdir(d)
    dest = os.path.join(d, b0)

    if not os.path.exists(dest):
        try:
            os.link(filename, dest)
        except OSError:
            shutil.copy(filename, dest)

    r = OrderedDict()
    r['filename'] = b0
    r['ctime'] = datetime.fromtimestamp(os.path.getctime(filename))
    r['upload_host'] = socket.gethostname()
    # no - otherwise it changes every time
    # r['upload_date'] = datetime.now()
    r['upload_node'] = get_ipfs_id()
    r['upload_user'] = getpass.getuser()
    info = os.path.join(d, 'upload_info1.yaml')
    with open(info, 'w') as f:
        y = yaml_dump_omaps(r)
        f.write(y)
    return d


class UnexpectedFormat(Exception):
    pass


MoreInfo = namedtuple('MoreInfo', 'ipfs ipfs_payload ipfs_info filename upload_host upload_node'
                      ' upload_user ctime size providers_payload providers_info')

INFO = 'upload_info1.yaml'


@memoize_simple
def find_more_information(ipfsi, h, find_provs=False):
    contents = ipfsi.ls(h, timeout="3s")
    timeout = "1h"
    if not INFO in contents:
        raise UnexpectedFormat(str(contents))

    try:
        info_data = ipfsi.get(h + '/' + INFO, timeout=timeout)
    except CmdException as e:
        if 'no link named' in e.res.stderr:
            raise UnexpectedFormat(e.res.stderr)
        raise

    try:
        info = yaml_load_omaps(info_data)
    except:
        raise UnexpectedFormat()

    try:
        filename = info['filename']
        ctime = info['ctime']
        upload_host = info['upload_host']
        upload_node = info['upload_node']
        upload_user = info['upload_user']
    except KeyError as e:
        msg = 'Invalid format: %s' % e
        raise UnexpectedFormat(msg)

    try:
        ipfs_info = contents[INFO].hash
        ipfs_payload = contents[filename].hash
        size = contents[filename].size
    except KeyError as e:
        raise UnexpectedFormat(str(e))
    ipfsi = IPFSInterface()

    if find_provs:
        providers_info = ipfsi.dht_findprovs(ipfs_info)
        providers_payload = ipfsi.dht_findprovs(ipfs_payload)
    else:
        providers_info = []
        providers_payload = []

    return MoreInfo(ipfs=h,
                    ipfs_payload=ipfs_payload,
                    ipfs_info=ipfs_info,
                    filename=filename,
                    ctime=ctime,
                    size=size,
                    providers_info=providers_info,
                    providers_payload=providers_payload,
                    upload_host=upload_host,
                    upload_node=upload_node,
                    upload_user=upload_user)


def add_ipfs_dir(dirname):
    cmd = ['ipfs', 'add', '-r', dirname]
#    print cmd
    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True)
    s = res.stdout.strip()
    lines = s.split('\n')
    out = lines[-1].split(' ')
    if (len(out) < 3 or out[0] != 'added' or not out[1].startswith('Qm')):
        msg = 'Invalid output for ipds:\n%s' % indent(res.stdout, ' > ')
        raise Exception(msg)
    hashed = out[1]
    return hashed
#
#


def get_ipfs_id():
    cmd = ['ipfs', 'id']
    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True,
                             display_stdout=False, display_stderr=False)
    data = json.loads(res.stdout.strip())
    return str(data['ID'])


class Queues():
    incoming = Queue()
    pinner_queue = Queue()
    outgoing_irc = Queue()
    outgoing_pub = Queue()
    outgoing = [outgoing_irc, outgoing_pub]
    to_summary_publisher = Queue()
    ipns_queue = Queue()


def duckietown_swarm_main():
    from duckietown_swarm.summary import publish_ipns
    args = sys.argv[1:]
    if not args:
        watch_dir = os.path.expanduser('~/shared-logs')
    else:
        watch_dir = args[0]

    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
    print('You can put any log file in the directory\n\n\t%s\n\nand it will be shared with the swarm.\n\n' % watch_dir)

    pubsub_reader = Process(target=pubsub_reader_process, args=())
    pubsub_reader.daemon = True
    pubsub_reader.start()  # Launch reader() as a separate python process

    p = Process(target=publish_ipns, args=())
    p.daemon = True
    p.start()

    pubsub_writer = Process(target=pubsub_writer_process, args=())
    pubsub_writer.daemon = True
    pubsub_writer.start()  # Launch reader() as a separate python process

    npinners = 10
    for i in range(npinners):
        reader_p = Process(target=pinner, args=(i,))
        reader_p.daemon = True
        reader_p.start()

    from .distributed_cache import brain

    cache_dir = os.path.join(watch_dir, '.cache')

    irc_process = Process(target=start_irc, args=(()))
    irc_process.daemon = True
    irc_process.start()

    if True:
        brain_process = Process(target=brain, args=(cache_dir,))
        brain_process.daemon = True
        brain_process.start()

    if True:
        watcher = Process(target=directory_watcher, args=((watch_dir,)))
        watcher.daemon = True
        watcher.start()

    if True:
        friendship = Process(target=pubsub_friendship, args=())
        friendship.daemon = True
        friendship.start()

    if True:
        from duckietown_swarm.summary import publisher_summary
        p = Process(target=publisher_summary, args=())
        p.daemon = True
        p.start()

    irc_process.join()


def start_irc():
    from duckietown_swarm.summary import get_at_least_one
    random.seed()
    channel = '#duckiebots'

    nickname = 'D_%s_' % (__version__) + str(random.randint(0, 100000))
    nickname = nickname.replace('.', '_')
    print('Using nickname %s' % nickname)

    c = SwarmBot(Queues.incoming, channel, nickname)
    while True:

        while True:
            attempt_start = time.time()
            c.admitted = False
            print('server list: %s' % [_.host for _ in c.server_list])
            c._connect()
            while not c.admitted:
                print('Waiting for welcome')
                time.sleep(1)
                c.reactor.process_once()

                delta = time.time() - attempt_start
                give_up = delta > 20
                if give_up:
                    print('giving up after %d s' % delta)
                    break
            if c.admitted:
                break
            print('Changing server')
            c.jump_server()

        c.disconnected = False

        while True:
            time.sleep(1.0)
            c.reactor.process_once(1.0)
            if c.disconnected:
                break

            xs = get_at_least_one(Queues.outgoing_irc, timeout=1.0)
            for x in xs:
                c.send_message(x)


def ipfs_pubsub_send(topic, message):
    cmd = ['ipfs', 'pubsub', 'pub', topic, message + '\n']
    system_cmd_result('.', cmd, raise_on_error=True)


if __name__ == "__main__":
    duckietown_swarm_main()
