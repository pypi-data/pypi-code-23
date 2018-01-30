# -*- coding: utf8 -*-
import boto3
import botocore
from hashlib import sha1

import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def _hex_to_filename(path, hex):
    """Takes a hex sha and returns its filename relative to the given path."""
    # os.path.join accepts bytes or unicode, but all args must be of the same
    # type. Make sure that hex which is expected to be bytes, is the same type
    # as path.
    if getattr(hex, 'decode', None) is not None:
        hex = hex.decode('ascii')

    if getattr(path, 'decode', None) is not None:
        path = path.decode('ascii')

    dir_name = hex[:2]
    file = hex[2:]
    # Check from object dir
    return os.path.join(path, dir_name, file)


def transfer_object(event, context):
    src_bucket = event['src_bucket']
    dest_bucket = event['dest_bucket']
    src_object = event['src_object']

    s3 = boto3.resource('s3')

    with StringIO() as f:
        s3.Bucket(src_bucket).download_fileobj(src_object, f)

        f.seek(0)

        h = sha1()
        h.update(f.getvalue())
        sha = h.hexdigest()

        dest_object = _hex_to_filename('objects', sha)

        s3.Bucket(dest_bucket).upload_fileobj(src_object, dest_object)

        return {
            'sha': sha
        }
