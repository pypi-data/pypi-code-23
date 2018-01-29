
import os
from random import randint
from secrets import token_urlsafe
import tempfile


def rand_fn(outdir):
    return os.path.join(outdir, '{}.txt'.format(token_urlsafe(4)))


def make_file(tmpdir, filesize=1024):
    fp = rand_fn(tmpdir)
    with open(fp, 'xb') as outfile:
        outfile.write(os.urandom(filesize))

    return fp


def test_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        print('tmpdir loc:')
        print(tmpdir)
        for _ in range(10):
            make_file(tmpdir)

        # for _ in range(NA):
        #     print('error')
