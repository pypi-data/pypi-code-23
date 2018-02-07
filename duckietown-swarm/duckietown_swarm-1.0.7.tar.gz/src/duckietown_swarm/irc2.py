#! /usr/bin/env python

from Queue import Empty
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

from conf_tools.utils.indent_string import indent
from conf_tools.utils.locate_files_imp import locate_files
from contracts import contract
import irc.bot  #@UnresolvedImport
from system_cmd import CmdException, system_cmd_result

from duckietown_swarm.distributed_cache import brain


#from easy_logs.ipfs_utils import MakeIPFS
def pinner():
    ## Read from the queue
    done = set()
    while True:
        msg = Queues.pinner_queue.get()
        # if msg == 'exit': break
        if msg in done:
            print('Pinner received %s twice' % msg)
            continue
        done.add(msg)

        cmd = ['ipfs', 'pin', 'add', '-r', '--timeout', '30s', msg]
#        print(" ".join(cmd))
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False)
        if res.ret != 0:
            print('Pinning %s: invalid file' % msg)
        else:
            print('Pinning %s: OK' % msg)
#            print(res.stdout)
#            print(res.stderr)
#        else:
#            print(' success')


def directory_watcher(watch_dir):
    seen = {}
    tmpdir = mkdtemp(prefix='swarm')

    def look_for_files(d, pattern='*'):
        if not os.path.exists(d):
            msg = 'Logs directory does not exist: %s' % d
            raise ValueError(msg)

        filenames = locate_files(d, pattern)
        for f in filenames:
            if not f in seen:

                try:
                    hashed = _add_file(f)
                    print('found local %s %s' % (hashed, f))
                    msg = {'mtype': 'advertise',
                           'details': {'bucket': 'files',
                                      'ipfs': hashed,
                                      'comment': "just found"}}
                    for q in Queues.outgoing + [Queues.incoming]:
                        q.put(msg)
                except Exception as e:
                    print('error adding %s' % f)
                    pass
    #    def _update_summary(self):
    #        h = get_summary(self.known, self.seen)
    #        print('summary: %s' % h)

    def _add_file(filename):
        d = setup_dir_for_file(tmpdir, filename)
        try:
            hashed = add_ipfs_dir(d)
            seen[filename] = hashed
            return hashed
        except CmdException as e:
            print(e)
            raise Exception()

    while True:
        look_for_files(watch_dir)
        time.sleep(5)


def pubsub_reader_process():
    cmd = ['ipfs', 'pubsub', 'sub', '--discover', 'duckiebots']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        # print('received pubsub: ' + line)
        try:
            j = json.loads(line)
            Queues.incoming.put(j)
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
#    print('IPFS ID: %s' % ID)
    # connect to mama duck
#    mama = 'QmW5P8PZhGYGoyGzAGZNKNTKrvbg8m7Wv4QF4o2ghYmuf9'
#    cmd = ['ipfs', 'swarm', 'connect', '--timeout', '30s', '/p2p-circuit/ipfs/' + mama]
#    system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False, display_stdout=False, display_stderr=False)

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
        print('Found %s Duckiebots in the hidden botnet.' % len(hosts))
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
        except OSError as e:
            if e.errno == 18:  # invalid cross-device
                shutil.copy(filename, dest)
            else:
                raise

    return d


def add_ipfs_dir(dirname):
    cmd = ['ipfs', 'add', '-r', dirname]
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
#def get_summary(known, seen):
#    m = MakeIPFS()
#    s = '<html><head></head><body><pre>\n'
#
#    s += '<h2>Mine</h2>'
#    for f, h in seen.items():
#        b = os.path.basename(f)
#        m.add_file(b, h, 0)
#        s += '\n<a href="%s">%s</a>' % (b, b)
#
#    s += '<h2>Others</h2>'
#    for h in known:
#        m.add_file(h, h, 0)
#        s += '\n<a href="%s">%s</a>' % (h, h)
#
#    s += '\n</pre></body>'
#
#    m.add_file_content('index.html', s)
#
#    return m.get_ipfs_hash()


def get_ipfs_id():
    cmd = ['ipfs', 'id']
    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True,
                             display_stdout=False, display_stderr=False)
    data = json.loads(res.stdout.strip())
    return data['ID']


class Queues():
    incoming = Queue()
    pinner_queue = Queue()
    outgoing_irc = Queue()
    outgoing_pub = Queue()
    outgoing = [outgoing_irc, outgoing_pub]


def duckietown_swarm_main():
    args = sys.argv[1:]
    if not args:
        watch_dir = os.path.expanduser('~/shared-logs')
    else:
        watch_dir = args[0]

#    home_dir = args[0]
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
    print('You can put any log file in the directory\n\n\t%s\n\nand it will be shared with the swarm.\n\n' % watch_dir)
#    print('watch_dir: %s' % watch_dir)
#    print('home_dir: %s' % home_dir)
#    if not os.path.exists(home_dir):
#        os.makedirs(home_dir)

    pubsub_reader = Process(target=pubsub_reader_process, args=())
    pubsub_reader.daemon = True
    pubsub_reader.start()  # Launch reader() as a separate python process

    pubsub_writer = Process(target=pubsub_writer_process, args=())
    pubsub_writer.daemon = True
    pubsub_writer.start()  # Launch reader() as a separate python process

    reader_p = Process(target=pinner, args=())
    reader_p.daemon = True
    reader_p.start()  # Launch reader() as a separate python process

    brain_process = Process(target=brain, args=())
    brain_process.daemon = True
    brain_process.start()

    irc_process = Process(target=start_irc, args=(()))
    irc_process.daemon = True
    irc_process.start()

    watcher = Process(target=directory_watcher, args=((watch_dir,)))
    watcher.daemon = True
    watcher.start()

    friendship = Process(target=pubsub_friendship, args=())
    friendship.daemon = True
    friendship.start()

    irc_process.join()


def start_irc():
    nickname = socket.gethostname() + '_' + str(random.randint(0, 100))
    channel = '#duckiebots'
#    delta = 20
    c = SwarmBot(Queues.incoming, channel, nickname)
    while True:

        while True:
            attempt_start = time.time()
            c.admitted = False
            c._connect()
            while not c.admitted:
                # print('Waiting for welcome')
                time.sleep(1)
                c.reactor.process_once()

                give_up = time.time() - attempt_start > 10
                if give_up:
                    break
            if c.admitted:
                break
            print('Changing server')
            c.jump_server()
            print('server list: %s' % [_.host for _ in c.server_list])

#        last_sent = time.time() - delta
        c.disconnected = False
        while True:
            time.sleep(1 + random.uniform(0, 1))

#            t = time.time()
#            if t > last_sent + delta:
##                c.look_for_files(watch_dir)
##                print('Mine: %s' % sorted(c.seen.values()))
##                print('Known: %s' % sorted(c.known))
#                last_sent = t

#            c.rebroadcast()
            c.reactor.process_once()
            if c.disconnected:
                break

            try:
                x = Queues.outgoing_irc.get(block=False, timeout=0.1)
                c.send_message(x)
            except Empty:
                pass


def ipfs_pubsub_send(topic, message):
    cmd = ['ipfs', 'pubsub', 'pub', topic, message + '\n']
    system_cmd_result('.', cmd, raise_on_error=True)


if __name__ == "__main__":
    duckietown_swarm_main()
