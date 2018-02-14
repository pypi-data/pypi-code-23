"""
This module enables working with gunzip to open gzip files

The reason for this module is the following benchmark:
- with python gzip decoded to text:
$ time ./flipkart_read_all_clickstream.py
real    4m23.271s
user    55m55.884s
sys     1m28.552s
- with pipe from zcat:
$ time ./flipkart_read_all_clickstream.py
real    3m13.042s
user    32m49.568s
sys     4m0.020s
- with pipe from zcat + decoding:
$ time ./flipkart_read_all_clickstream.py
real    3m19.863s
user    32m2.292s
sys     4m17.796s
"""
import gzip
import subprocess

from typing import Any, Union

import sys


def is_2():
    return sys.version_info[0] == 2


# noinspection PyShadowingBuiltins
def open(filename, mode="rb", use_process=False, encoding='utf-8', newline=None):
    # type: (str, str, bool, str, Union[str, None]) -> Any
    if "r" in mode:
        if use_process:
            args = [
                "/bin/zcat",
                filename,
            ]
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            if "b" in mode:
                return process.stdout
            if "t" in mode:
                if is_2():
                    # import io
                    # return io.TextIOWrapper(process.stdout.fileno(), encoding=encoding, newline=newline)
                    import io
                    return io.open(process.stdout.fileno(), encoding=encoding, newline=newline, closefd=False)
                    # import codecs
                    # return codecs.getreader(encoding=encoding)(process.stdout)
                else:
                    import io
                    return io.TextIOWrapper(process.stdout, encoding=encoding, newline=newline)
            raise ValueError("please specify t or b in mode")
        else:
            if is_2():
                # in python2 gzip.open does not have a 'newline' parameter or the 'encoding'
                # parameter...
                if 'b' in mode:
                    return gzip.open(filename, mode=mode)
                else:
                    handle = gzip.open(filename, mode='rb')
                    import codecs
                    return codecs.getreader(encoding=encoding)(handle)
            else:
                return gzip.open(filename, encoding=encoding, mode=mode, newline=newline)
    if "w" in mode:
        if is_2():
            return gzip.open(filename, mode=mode, newline=newline)
        else:
            return gzip.open(filename, encoding=encoding, mode=mode, newline=newline)


