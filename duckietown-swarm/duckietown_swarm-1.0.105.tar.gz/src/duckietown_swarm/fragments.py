'''

{'fragment': 0, 'n': 10, 'sha256_base58': 'ckodokocdk', 'chunk_base58': ''}


'''
from collections import OrderedDict, defaultdict
import json

from base58 import b58encode, b58decode
from contracts import contract
from contracts.utils import raise_desc

from .dcache import get_sha256_base58


@contract(s0=str, max_chunk_length='int', returns='list(str)')
def fragmentize(s0, max_chunk_length):
    # first, divide in chunks
    chunks = []
    s = s0
    while len(s) > 0:
        chunk = s[:max_chunk_length]
        chunks.append(chunk)
        s = s[max_chunk_length:]

    assert ''.join(chunks) == s0, (chunks, s0)

    checksum = get_sha256_base58(s0)
    msgs = []
    for i, chunk in enumerate(chunks):
        od = OrderedDict()
        od['fragment'] = i
        od['n'] = len(chunks)
        od['sha256_base58'] = checksum
        od['chunk_base58'] = b58encode(chunk)
        j = json.dumps(od)
        msgs.append(j)
    return msgs


class Assembler():

    def __init__(self):

        # sha -> i -> message
        self.chunks = defaultdict(lambda: {})
        self.output = []

    def push(self, s):
        try:
            j = json.loads(s)
        except ValueError:
            msg = 'Cannot read string of size %s: %r' % (len(s), s)
            print(msg)
            return

        if 'fragment' in j:
            self.chunks[j['sha256_base58']][j['fragment']] = j
        else:
            self.output.append(s)
        self.check_complete()

    def pop(self):
        res = self.output
        self.output = []
        return res

    def check_complete(self):
        for c, fragment2chunks in list(self.chunks.items()):
            try:
                s = assemble_chunks(fragment2chunks)
            except Corrupted as e:
                print(e)
                self.chunks.pop(c)
            except Incomplete as e:
                pass
            else:
                self.output.append(s)
                self.chunks.pop(c)


class Corrupted(Exception):
    pass


class Incomplete(Exception):
    pass


def assemble_chunks(fragment2chunk):
    one = list(fragment2chunk.values())[0]
    n = one['n']
    s = ''
    for i in range(n):
        if not i in fragment2chunk:
            raise Incomplete()

        chunk = fragment2chunk[i]
        si = b58decode(chunk['chunk_base58'])
        s += si

    checksum = get_sha256_base58(s)
    if checksum != one['sha256_base58']:
        raise_desc(Corrupted, 'Failed checksum', s=s.__repr__())
    return s
