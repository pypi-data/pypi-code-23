from collections import OrderedDict, namedtuple
from duckietown_swarm.spawn_ipfs import get_ipfs_executable
import json
import os
import sys
import time

from contracts import contract, new_contract
from contracts.utils import check_isinstance, raise_wrapped
from contracts.utils import indent
from system_cmd import CmdException, system_cmd_result

from .utils import memoize_simple, tmpfile


class Timeout(Exception):
    pass


class InvalidHash(Exception):
    pass


class CouldNotPin(Exception):
    pass


IPFS_ls_entry = namedtuple('IPFS_ls_entry', 'name hash size')


@new_contract
def multihash(mh):
    check_isinstance(mh, str)
    return mh.startswith('Qm')


class IPFSInterface(object):

    def __init__(self, ipfs_path):
        if ipfs_path is None:
            d = os.path.expanduser('~/shared-logs/.cache/.ipfs')
            if os.path.exists(d):
                ipfs_path = d
            else:
                if 'IPFS_PATH' in os.environ:
                    ipfs_path = os.environ['IPFS_PATH']
                else:
                    ipfs_path = os.path.expanduser('~/.ipfs')
        self.ipfs_path = ipfs_path
        self.providers_ttl = 120
        self.providers_cache = {}
        self.debug = False

    @memoize_simple
    def get_executable(self):
        return get_ipfs_executable(self.ipfs_path)

    @memoize_simple
    def version(self):
        cmd = ['ipfs', '--version']
        res = self._cmd(cmd)
        version = res.stdout
        version = version.replace('ipfs', '')
        version = version.replace('version', '')
        version = version.strip()
        print('Detected version %r' % version)
        return version

    def _get_env(self):
        env = os.environ.copy()
        if self.ipfs_path is not None:
            env['IPFS_PATH'] = self.ipfs_path
        return env

    def _cmd(self, cmd):
        if cmd[0] == 'ipfs':
            cmd[0] = self.get_executable()

        if self.debug:
            print('$ %s' % " ".join(cmd))
        else:
            sys.stderr.write('.')
        t0 = time.time()
        res = system_cmd_result('.', cmd, raise_on_error=True, env=self._get_env())

        delta = time.time() - t0
        if self.debug:
            print('took %5.2f s: $ %s' % (delta, " ".join(cmd)))
        return res

    def get_keys(self):
        ipfs = self.get_executable()
        cmd = [ipfs, 'key', 'list', '-l']
        res = self._cmd(cmd)
        #print res.stdout.__repr__()
        lines = res.stdout.strip().split('\n')
        res = OrderedDict()
        for l in lines:
            tokens = l.strip().split(' ')
            assert len(tokens) == 2, tokens
            res[tokens[1]] = tokens[0]
        return res

    def gen_key(self, name, key_type, key_size):
        cmd = ['ipfs', 'key', 'gen', '--type', key_type, '--size', str(key_size), name]
        res = self._cmd(cmd)
        ipfs_hash = res.stdout.strip()
        return ipfs_hash

    def publish(self, key_name, ipfs_hash, timeout='60s'):
        cmd = ['ipfs', 'name', 'publish', '--timeout', timeout, '--key', key_name, ipfs_hash]
        _res = self._cmd(cmd)

    def pin_add(self, mh, recursive=True, timeout=None):
        cmd = ['ipfs', 'pin', 'add']
        if recursive:
            cmd.append('-r')
        if timeout is not None:
            cmd.extend(['--timeout', timeout])
        cmd.append(mh)
        res = self._cmd(cmd)
        if res.ret != 0:
            raise CouldNotPin(str(res))

    def pin_ls(self):
        cmd = ['ipfs', 'pin', 'ls']
        res = self._cmd(cmd)
        recursive = set()
        indirect = set()
        for line in res.stdout.strip().split('\n'):
            tokens = line.split(' ')
            hashed = tokens[0]
            if tokens[1] == 'recursive':
                recursive.add(hashed)
            elif tokens[1] == 'indirect':
                indirect.add(hashed)
            else:
                assert False, line

        return recursive, indirect

    def dht_findprovs(self, ipfs_hash, timeout="1s"):
        if ipfs_hash in self.providers_cache:
            t, result = self.providers_cache[ipfs_hash]
            elapsed = time.time() - t
            if elapsed < self.providers_ttl:
                return result
        result = self._dht_findprovs(ipfs_hash, timeout)
        self.providers_cache[ipfs_hash] = time.time(), result
        return result

    def _dht_findprovs(self, ipfs_hash, timeout):
        cmd = ['ipfs', 'dht', 'findprovs', '--timeout', timeout, ipfs_hash]
        try:
            res = self._cmd(cmd)
        except CmdException as e:
            res = e.res
        options = res.stdout.strip().split('\n')
        options = [x for x in options if x]
        return options

    @memoize_simple
    def object_get(self, h, timeout=None):
        cmd = ['ipfs', 'object']
        if timeout is not None:
            cmd.extend([ '--timeout', timeout])
        cmd.extend(['get', h])

        try:
            res = self._cmd(cmd)
        except CmdException as e:
            raise InvalidHash(e.res.stderr)
        return res.stdout

    @memoize_simple
    def get(self, mh, timeout="1h"):
        with tmpfile('.ipfs_data') as f:
            cmd = ['ipfs', 'get', '--timeout', timeout, '-o', f, mh]
            try:
                _res = self._cmd(cmd)
            except CmdException as e:
                if e.res.ret == 1 and 'request canceled' in e.res.stderr:
                    msg = 'Could not get %s with timeout %s' % (mh, timeout)
                    raise_wrapped(Timeout, e, msg)
                print('exc %s %r' % (e.res.ret, e.res.stderr))
                raise
            data = open(f).read()
            return data

    def ls(self, h, timeout="10s"):
    #    {"Links":[{"Name":"FILE2","Hash":"QmUtkGLvPf63NwVzLPKPUYgwhn8ZYPWF6vKWN3fZ2amfJF","Size":14},
    # {"Name":"upload_info1.yaml","Hash":"QmeiuS7VWRaUQTmva3UMgggCCEDisgtLWPwxFnJ1kCGaDJ","Size":214}],"Data":"\u0008\u0001"}
        data = self.object_get(h, timeout=timeout)
        d = json.loads(data)
        entries = OrderedDict()
        for entry in d['Links']:
            entries[str(entry['Name'])] = \
                IPFS_ls_entry(str(entry['Name']), str(entry['Hash']), entry['Size'])
        return entries

    def add_bytes(self, s):
        return self.get_hash_for_bytes(s)

    def block_put(self, s):
        ipfs = self.get_executable()
        cmd = [ipfs, 'block', 'put']
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True, display_stdout=False, display_stderr=False,
                                write_stdin=s, env=self._get_env())
        token = res.stdout.strip()
        return token

    @memoize_simple
    def _get_ipfs_id_data(self):
        cmd = ['ipfs', 'id']
        res = self._cmd(cmd)

        data = json.loads(res.stdout.strip())
        return data

    def stats_bw(self):
        cmd = ['ipfs', 'stats', 'bw']
        res = self._cmd(cmd)
        return res.stdout.strip()

    @memoize_simple
    def ipfs_id(self):
        data = self._get_ipfs_id_data()
        return str(data['ID'])

    @memoize_simple
    @contract(returns='list(str)')
    def get_addresses(self):
        data = self._get_ipfs_id_data()
        if data['Addresses']:
            return map(str, data['Addresses'])
        else:
            return []

    def p2p_listener_open(self, name, address):
        cmd = ['ipfs', 'p2p', 'listener', 'ls']
        res = self._cmd(cmd)
        already = name in res.stdout
        if already:
            cmd = ['ipfs', 'p2p', 'listener', 'close', name]
            res = self._cmd(cmd)

        cmd = ['ipfs', 'p2p', 'listener', 'open', name, address]
        res = self._cmd(cmd)
        return json.loads(res.stdout.strip())

    def swarm_connect(self, peer, timeout='10s'):
        cmd = ['ipfs', 'swarm', '--timeout', timeout, 'connect', peer]
        res = self._cmd(cmd)
        print(res.stdout)

    def object_put(self, data):
        ipfs = self.get_executable()
        cmd = [ipfs, 'object', 'put']
        cwd = '.'
        res = system_cmd_result(cwd, cmd, raise_on_error=True,
                                write_stdin=data, env=self._get_env())
        hashed = res.stdout.split()[1]
        assert 'Qm' in hashed, hashed
        return hashed

    def add(self, s):
        ipfs = self.get_executable()
        cmd = [ipfs, 'add']
        cwd = '.'
        res = system_cmd_result(cwd, cmd, raise_on_error=True,
                                write_stdin=s, env=self._get_env())
        hashed = res.stdout.split()[1]
        assert 'Qm' in hashed, hashed
        return hashed

    get_hash_for_bytes = add

    def add_ipfs_dir(self, dirname):
        ipfs = self.get_executable()
        cmd = [ipfs, 'add', '-r', dirname]
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True,
                                env=self._get_env())
        s = res.stdout.strip()
        lines = s.split('\n')
        out = lines[-1].split(' ')
        if (len(out) < 3 or out[0] != 'added' or not out[1].startswith('Qm')):
            msg = 'Invalid output for ipds:\n%s' % indent(res.stdout, ' > ')
            raise Exception(msg)
        hashed = out[1]
        return hashed

    def get_tree_builder(self):
        return MakeIPFS3(self)


class MakeIPFS3(object):

    def __init__(self, ipfsi):
        self.ipfsi = ipfsi
        self.links = []
        self.total_file_size = 0

    def add_file(self, filename, mh, size):
        x = {'Name': filename, 'Hash': mh, "Size": size}
        self.links.append(x)
        self.total_file_size += size

    @contract(filename=str, s=str)
    def add_file_content(self, filename, s):
        # TODO: check filename
        mh = self.ipfsi.get_hash_for_bytes(s)
        self.add_file(filename, mh, len(s))

    def get_dag(self):
        result = {'Data': u"\u0008\u0001", 'Links': self.links}
        return result

    def total_size(self):
        return self.total_file_size

    def as_json(self):
        dag = self.get_dag()
        dag_json = json.dumps(dag)
        return dag_json

    @contract(returns='multihash')
    def get_hash(self):
        return self.ipfsi.object_put(self.as_json())

#
#
#def ipfs_pubsub_send(topic, message):
#    cmd = ['ipfs', 'pubsub', 'pub', topic, message + '\n']
#    system_cmd_result('.', cmd, raise_on_error=True)
