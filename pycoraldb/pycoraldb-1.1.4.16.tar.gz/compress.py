#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import gzip
import StringIO


def smart_compress_gzip(data):
    ret = data
    if len(data) >= 1024:
        buf = StringIO.StringIO()
        f = gzip.GzipFile(fileobj=buf, mode='wb')
        f.write(data)
        f.flush()
        f.close()
        zip_data = buf.getvalue()
        buf.close()
        if len(zip_data) < len(data):
            ret = zip_data
    return ret


def smart_uncompress_gzip(data):
    ret = data
    if len(data) >= 2 and data[0] == 0x1F and data[1] == 0x8B:
        buf = StringIO.StringIO(data)
        f = gzip.GzipFile(fileobj=buf)
        ret = f.read()
        f.close()
    return ret


if __name__ == '__main__':
    data = 'abc'
    s = smart_uncompress_gzip(smart_compress_gzip(data))
    if data == s:
        print 'test ok: %s' % (s)
    else:
        print 'test failed: %s' % (s)
