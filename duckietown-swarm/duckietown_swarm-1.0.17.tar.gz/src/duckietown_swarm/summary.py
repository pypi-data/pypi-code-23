from Queue import Empty
from duckietown_swarm.ipfs_utils import IPFSInterface
from duckietown_swarm.irc2 import find_more_information, UnexpectedFormat, \
    InvalidHash
import json
import time

from system_cmd.meat import system_cmd_result


def get_at_least_one(queue):
    s = []
    while True:
        try:
            block = len(s) == 0
            x = queue.get(block=block)
            s.append(x)
        except Empty:
            break
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

    time.sleep(20)
    while True:
        hashes = get_at_least_one(Queues.to_summary_publisher)
        print('Creating summary for %d more' % (len(hashes)))
        known.update(hashes)

        summary_hash = get_summary(known)
        ipfsi.publish(KEY_NAME, summary_hash)
        print('published to %s ' % path)


def get_summary(known):
    m = MakeIPFS2()
    s = '<html><head></head><body><pre>\n'

    found = []
    others = []
    invalid = []
    for k in known:
        try:
            f = find_more_information(k)
            found.append(f)
        except UnexpectedFormat:
            others.append(k)
        except InvalidHash:
            invalid.append(k)

    s += '<h2>Good uploads</h2>'
    already = set()
    found = sorted(found, key=lambda _: _.ctime)
    for f in found:
        if f.ipfs_payload in already:
            continue
        already.add(f.ipfs_payload)
        m.add_file(f.ipfs_payload, f.ipfs_payload, f.size)
        m.add_file(f.ipfs_info, f.ipfs_info, 0)
        s += '\n'
        s += '<a href="%s">info</a>' % (f.ipfs_info)
        s += ' <a href="/ipfs/%s">raw</a>' % (f.ipfs)
        s += ' ' + str(f.ctime)[:16]
        s += ' %5d MB' % (f.size / (1000.0 * 1000))
        s += ' <a href="%s">%s</a>' % (f.ipfs_payload, '%20s' % f.filename)
        s += ' uploaded by %s : %s @ %s' % (f.upload_node, f.upload_user, f.upload_host)

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
