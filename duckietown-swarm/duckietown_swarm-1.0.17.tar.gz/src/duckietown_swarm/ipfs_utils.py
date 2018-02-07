from collections import OrderedDict

from system_cmd.meat import system_cmd_result


class IPFSInterface():

    def _cmd(self, cmd):
        print('$ %s' % " ".join(cmd))
        res = system_cmd_result('.', cmd, raise_on_error=True)
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
