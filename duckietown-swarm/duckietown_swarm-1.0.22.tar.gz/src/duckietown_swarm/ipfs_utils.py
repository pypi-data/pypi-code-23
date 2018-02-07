from collections import OrderedDict, namedtuple
from duckietown_swarm.utils import memoize_simple, tmpfile
import json
import time

from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException


class InvalidHash(Exception):
    pass


IPFS_ls_entry = namedtuple('IPFS_ls_entry', 'name hash size')


class IPFSInterface():

    def __init__(self):
        self.providers_ttl = 120
        self.providers_cache = {}
        self.debug = False

    def _cmd(self, cmd):
        if self.debug:
            print('$ %s' % " ".join(cmd))
        t0 = time.time()
        res = system_cmd_result('.', cmd, raise_on_error=True)

        delta = time.time() - t0
        if self.debug:
            print('took %5.2f s: $ %s' % (delta, " ".join(cmd)))
        return res

    def get_keys(self):
        cmd = ['ipfs', 'key', 'list', '-l']
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
        res = self._cmd(cmd)

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
        return res.stdout.strip().split('\n')

    @memoize_simple
    def object_get(self, h):
        cmd = ['ipfs', 'object', 'get', h]
        try:
            res = self._cmd(cmd)
        except CmdException as e:
            raise InvalidHash(e.res.stderr)
        return res.stdout

    @memoize_simple
    def get(self, h):
        with tmpfile('.ipfs_data') as f:
            cmd = ['ipfs', 'get', '-o', f, h]
            res = self._cmd(cmd)
            data = open(f).read()
            return data

    def ls(self, h):
    #    {"Links":[{"Name":"FILE2","Hash":"QmUtkGLvPf63NwVzLPKPUYgwhn8ZYPWF6vKWN3fZ2amfJF","Size":14},
    # {"Name":"upload_info1.yaml","Hash":"QmeiuS7VWRaUQTmva3UMgggCCEDisgtLWPwxFnJ1kCGaDJ","Size":214}],"Data":"\u0008\u0001"}
        data = self.object_get(h)
        d = json.loads(data)
        entries = OrderedDict()
        for entry in d['Links']:
            entries[str(entry['Name'])] = \
                IPFS_ls_entry(str(entry['Name']), str(entry['Hash']), entry['Size'])
        return entries
