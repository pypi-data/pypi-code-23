from Queue import Empty
from datetime import datetime
import json
import socket
import time

from system_cmd import system_cmd_result, CmdException

from .ipfs_utils import IPFSInterface, InvalidHash
from .irc2 import find_more_information, UnexpectedFormat


def get_at_least_one(queue, timeout):
    """ This waits for one, and then waits at most timeout. """
    s = []
    t0 = time.time()
    while True:
        try:
            block = len(s) == 0
            x = queue.get(block=block, timeout=timeout)
            s.append(x)

            if time.time() < t0 + timeout:
                wait = t0 + timeout - time.time()
                time.sleep(wait)
        except Empty:
            break

    T = time.time() - t0
    if False:
        print('Got %s objects after %.1f s (timeout %.1f s)' % (len(s), T, timeout))
    return s


def publisher_summary():
    from duckietown_swarm.irc2 import Queues
    known = set()

    ipfsi = IPFSInterface()

    KEY_NAME = 'summary'
    keys = ipfsi.get_keys()
    if not KEY_NAME in keys:
        ipfsi.gen_key(KEY_NAME, 'rsa', 2048)
        keys = ipfsi.get_keys()

    path = '/ipns/' + keys[KEY_NAME]
    print('You will see my summaries at %s' % path)

    previous_hash = None
    while True:
        #print('summary')
        timeout = 5
#
#        n0 = len(known)
#        t0 = time.time()
        hashes = get_at_least_one(Queues.to_summary_publisher, timeout)
        changes = 0
        for x in hashes:
#            print('x: %s' % x)
            what, ipfs_hash = x
            if what == 'add':
                if not ipfs_hash in known:
                    print('publisher: adding %s' % ipfs_hash)
                    known.add(ipfs_hash)
                    changes += 1
            elif what == 'remove':
                if ipfs_hash in known:
                    known.remove(ipfs_hash)
                    changes += 1
                    print('publisher: remove %s' % ipfs_hash)
            else:
                assert False, x

        if changes == 0:
            continue
        #print('get_at_least_one: %.1f s' % (time.time() - t0))

        print('Creating summary for %d more, %d changes' % (len(known), changes))

        summary_hash = get_summary(ipfsi, known, permanent=path)
        print('summary: %s' % summary_hash)

        if previous_hash != summary_hash:
            print('summary hash: %s' % summary_hash)

            if False:
                try:
                    ipfsi.publish(KEY_NAME, summary_hash)
                except CmdException as e:
                    print(e)  # XXX

                print('published /ipns/%s -> /ipfs/%s ' % (keys[KEY_NAME], summary_hash))

            previous_hash = summary_hash

            msg = {'mtype': 'summary', 'details': {'ipfs': summary_hash}}

            for q in [Queues.incoming ] + Queues.outgoing:
                q.put(msg, block=False)


def get_summary(ipfsi, known, permanent):
    from duckietown_swarm.irc2 import advertise_invalid
    m = MakeIPFS2()
    s = '<html><head></head><body><pre>\n'

    s += '\n Created: %s' % str(datetime.now())[:16]
    s += '\n Host: %s' % socket.gethostname()
    s += '\n Permanent path: <a href="%s">%s</a>' % (permanent, permanent)

    s += '\n'
    found = []
    others = []
    invalid = []
    for k in known:
        try:
            f = find_more_information(ipfsi, k)
            found.append(f)
        except UnexpectedFormat:
            others.append(k)
        except InvalidHash:
            invalid.append(k)

    s += '<h2>Good uploads</h2>'
    already = set()
    redundant = []
    found = sorted(found, key=lambda _: _.ctime)

    def description(f):
        ss = ''
        ss += '<a href="/ipfs/%s">info</a>' % (f.ipfs_info)
        ss += ' <a href="/ipfs/%s">raw</a>' % (f.ipfs)
        ss += ' providers %3d %3d' % (len(f.providers_info), len(f.providers_payload))
        ss += ' ' + str(f.ctime)[:16]
        ss += ' %5d MB' % (f.size / (1000.0 * 1000))
        ss += ' <a href="/ipfs/%s">%s</a>' % (f.ipfs_payload, '%20s' % f.filename)
        ss += ' uploaded by %s : %s @ %s' % (f.upload_node, f.upload_user, f.upload_host)
        return ss

    for f in found:
        if f.ipfs_payload in already:
            redundant.append(f)
            continue
        already.add(f.ipfs_payload)
        m.add_file(f.ipfs_payload, f.ipfs_payload, f.size)
        m.add_file(f.ipfs_info, f.ipfs_info, 0)
        s += '\n' + description(f)

    if redundant:
        s += '<h2>Different uploads of same payload</h2>'
        for h in redundant:
            s += '\n' + description(h)

            advertise_invalid(h.ipfs, comment="redundant")

    if others:
        s += '<h2>Other uploads</h2>'
        for h in others:
            m.add_file(h, h, 0)
            s += '\n<a href="%s">%s</a>' % (h, h)

    if invalid:
        s += '<h2>Invalid hashes</h2>'
        for h in invalid:
            s += '\n' + h

    s += '\n</pre></body>'

    m.add_file_content('index.html', s)

    return m.get_ipfs_hash()


class MakeIPFS2(object):

    def __init__(self):
        self.links = []
        self.total_file_size = 0

    def add_file(self, filename, ipfs, size):
        x = {'Name': filename, 'Hash': ipfs, "Size": size}
        self.links.append(x)
        self.total_file_size += size

    def add_file_content(self, filename, s):
        hashed = get_hash_for_bytes_(s)
        self.add_file(filename, hashed, len(s))

    def get_dag(self):
        result = {'Data': u"\u0008\u0001", 'Links': self.links}
        return result

    def total_size(self):
        return self.total_file_size

    def get_ipfs_hash(self):
        dag = self.get_dag()
        dag_json = json.dumps(dag)

        cmd = ['ipfs', 'object', 'put']
        cwd = '.'
        res = system_cmd_result(cwd, cmd, raise_on_error=True,
                                write_stdin=dag_json)
        hashed = res.stdout.split()[1]
        assert 'Qm' in hashed, hashed
        return hashed


def get_hash_for_bytes_(s):
    cmd = ['ipfs', 'add']
    cwd = '.'
    res = system_cmd_result(cwd, cmd, raise_on_error=True,
                            write_stdin=s)
    hashed = res.stdout.split()[1]
    assert 'Qm' in hashed, hashed
    return hashed
