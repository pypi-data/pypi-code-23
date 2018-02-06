#! /usr/bin/env python

import json
from multiprocessing import Process, Queue
import os
import random
import shutil
import socket
import sys
from tempfile import mkdtemp
import time

import duckietown_utils as dtu
from duckietown_utils.locate_files_impl import locate_files
from duckietown_utils.system_cmd_imp import system_cmd_result
import irc.bot  #@UnresolvedImport


def pinner(queue):
    ## Read from the queue
    while True:
        msg = queue.get()  # Read from the queue and do nothing
        if msg == 'exit': break
#        print('received %s' % msg)
        cmd = ['ipfs', 'pin', 'add', '-r', '--timeout', '30s', msg]
        print(" ".join(cmd))
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False)
        if res.ret != 0:
            print(res.stdout)
            print(res.stderr)
        else:
            print(' success')


class SwarmBot(irc.bot.SingleServerIRCBot):

    def __init__(self, queue, channel, nickname):
        servers = [
                ('frankfurt.co-design.science', 6667),
                ('192.168.134.1', 6667),
        ]

        irc.bot.SingleServerIRCBot.__init__(self, servers, nickname, nickname)
        self.target = channel
        self.queue = queue

        # my files
        self.seen = {}
        # others
        self.known = set()
        # last mentions
        self.last_mentions = {}
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

        print('recv: ' + s)

        try:
            j = json.loads(s)
        except ValueError:
            return

        if j['mtype'] == 'advertise':
            ipfs = j['details']['ipfs']
            ipfs = str(ipfs)

            self.last_mentions[ipfs] = time.time()

            if not ipfs in list(self.seen.values()):
                if not ipfs in self.known:
#                    print('Somebody told me about %s' % ipfs)
                    self.known.add(ipfs)
                    self.queue.put(ipfs)

    def on_privmsg(self, c, e):
        self._handle(c, e)

    def on_welcome(self, connection, event):
        print('welcome message from %s: \n%s' % (connection.server, " ".join(event.arguments)))
        connection.join(self.target)
        self.admitted = True

    def on_join(self, _c, _e):
        users = self.channels[self.target].users()
        self.nusers = len(users)
        print('current users: %s' % users)

    def on_disconnect(self, _c, event):
        print('on_disconnect..', event.__dict__)
        self.disconnected = True

    def send_message(self, to, mtype, details, target=None):
        a = {  #'version': 1, 'to': to,
             'mtype': mtype, 'details': details}
        json_string = json.dumps(a)
        if target is None:
            target = self.target
        self.connection.privmsg(target, json_string)
        self.last_broadcast = time.time()

        print('sent: ' + json_string)

    def look_for_files(self, d, pattern='*'):
        if not os.path.exists(d):
            msg = 'Logs directory does not exist: %s' % d
            raise ValueError(msg)

        filenames = locate_files(d, pattern)
        for f in filenames:
            if not f in self.seen:
                self._add_file(f)

    def rebroadcast(self):
        h = list(set(list(self.seen.values()) + list(self.known)))

        def key(x):
            if x in self.last_mentions:
                return self.last_mentions[x]
            else:
                return 0

        sort = sorted(h, key=key)
        for hashed in sort:
            self._consider_broadcasting(hashed)

    def _consider_broadcasting(self, hashed):
        # suppose we want to have a target rate of
        target_rate = 0.33  # messages/s
        # then if we know there are
        nusers = self.nusers
        # on average each one should transmit
        min_interval = target_rate / nusers

        min_interval = max(min_interval, 10)

#        max_delta = 30 + self.lateness

        max_delta = 0  # always
        if not hashed in self.last_mentions:
            do = True
            delta = -1

#            print('%s rebroadcasting because never seen' % (hashed))
        else:
            delta = time.time() - self.last_mentions[hashed]
            do = delta > max_delta
#            if do:
#                print('%s rebroadcasting because delta = %s' % (hashed, delta))
        if do:
            time_since = time.time() - self.last_broadcast
            if time_since > min_interval:
                self.send_message(['all'], 'advertise', {'ipfs': hashed,
                                                         'comment': "rebroadcast (after %.1f s)" % delta})
                self.last_mentions[hashed] = time.time()

    def _add_file(self, filename):
        d = setup_dir_for_file(self.tmpdir, filename)
        hashed = add_ipfs_dir(d)
        self.seen[filename] = hashed


def setup_dir_for_file(tmpdir, filename):
    b0 = os.path.basename(filename)
    b = b0.replace('.', '_')
    d = os.path.join(tmpdir, b)
    if not os.path.exists(d):
        os.mkdir(d)
    dest = os.path.join(d, b0)

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
        msg = 'Invalid output for ipds:\n%s' % dtu.indent(res.stdout, ' > ')
        raise Exception(msg)
    hashed = out[1]
    return hashed


def duckietown_swarm_main():
    args = sys.argv[1:]
    watch_dir = args[1]
    home_dir = args[0]

    print('watch_dir: %s' % watch_dir)
    print('home_dir: %s' % home_dir)

    if not os.path.exists(home_dir):
        os.makedirs(home_dir)
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)

    cmd = ['ipfs', 'swarm', 'connect', '--timeout', '30s',
           '/p2p-circuit/ipfs/QmW5P8PZhGYGoyGzAGZNKNTKrvbg8m7Wv4QF4o2ghYmuf9']
    system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False, display_stdout=True, display_stderr=True)
    queue = Queue()
    reader_p = Process(target=pinner, args=((queue),))
    reader_p.daemon = True
    reader_p.start()  # Launch reader() as a separate python process

    nickname = socket.gethostname() + '_' + str(random.randint(0, 100))
    channel = '#duckiebots'

    delta = 20
    c = SwarmBot(queue, channel, nickname)
    while True:

        while True:
            attempt_start = time.time()
            c.admitted = False
            c._connect()
            while not c.admitted:
                print('Waiting for welcome')
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

        last_sent = time.time() - delta
        c.disconnected = False
        while True:
            time.sleep(1 + random.uniform(0, 1))

            t = time.time()
            if t > last_sent + delta:
                c.look_for_files(watch_dir)
#                print('Mine: %s' % sorted(c.seen.values()))
#                print('Known: %s' % sorted(c.known))
                last_sent = t

            c.rebroadcast()
            c.reactor.process_once()
            if c.disconnected:
                break

    queue.put('exit')
    pinner.join()


if __name__ == "__main__":
    duckietown_swarm_main()
