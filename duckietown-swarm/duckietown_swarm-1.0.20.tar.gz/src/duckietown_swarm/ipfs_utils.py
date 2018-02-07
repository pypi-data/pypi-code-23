from collections import OrderedDict
import time

from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException


class IPFSInterface():

    def __init__(self):
        self.providers_ttl = 120
        self.providers_cache = {}

    def _cmd(self, cmd):
#        print('$ %s' % " ".join(cmd))
        res = system_cmd_result('.', cmd, raise_on_error=True)
#        print res.stdout
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

    def publish(self, key_name, ipfs_hash):
        cmd = ['ipfs', 'name', 'publish', '--key', key_name, ipfs_hash]
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
