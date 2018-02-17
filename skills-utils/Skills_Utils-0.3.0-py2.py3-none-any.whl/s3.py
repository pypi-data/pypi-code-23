"""
Common S3 utilities
"""
import boto
import json
import logging
import os


def split_s3_path(path):
    """
    Args:
        path: (str) an s3 path including a bucket
            (bucket_name/prefix/prefix2)
    Returns:
        A tuple containing the bucket name and full prefix)
    """
    return path.split('/', 1)


def upload(s3_conn, filepath, s3_path):
    """Uploads the given file to s3

    Args:
        s3_conn: (boto.s3.connection) an s3 connection
        filepath (str) the local filename
        s3_path (str) the destination path on s3
    """
    bucket_name, prefix = split_s3_path(s3_path)
    bucket = s3_conn.get_bucket(bucket_name)
    filename = os.path.basename(filepath)

    key = boto.s3.key.Key(
        bucket=bucket,
        name='{}/{}'.format(prefix, filename)
    )
    logging.info('uploading from %s to %s', filepath, key)
    key.set_contents_from_filename(filepath)


def upload_dict(s3_conn, s3_prefix, data_to_sync):
    """Syncs a dictionary to an S3 bucket, serializing each value in the
    dictionary as a JSON file with the key as its name.

    Args:
        s3_conn: (boto.s3.connection) an s3 connection
        s3_prefix: (str) the destination prefix
        data_to_sync: (dict)
    """
    bucket_name, prefix = split_s3_path(s3_prefix)
    bucket = s3_conn.get_bucket(bucket_name)

    for key, value in data_to_sync.items():
        full_name = '{}/{}.json'.format(prefix, key)
        s3_key = boto.s3.key.Key(
            bucket=bucket,
            name=full_name
        )
        logging.info('uploading key %s', full_name)
        s3_key.set_contents_from_string(json.dumps(value))


def download(s3_conn, out_filename, s3_path):
    """Downloads the given s3_path

    Args:
        s3_conn (boto.s3.connection) a boto s3 connection
        out_filename (str) local filename to save the file
        s3_path (str) the source path on s3
    """
    bucket_name, prefix = split_s3_path(s3_path)
    bucket = s3_conn.get_bucket(bucket_name)
    key = boto.s3.key.Key(
        bucket=bucket,
        name=prefix
    )
    logging.info('loading from %s into %s', key, out_filename)
    key.get_contents_to_filename(out_filename, cb=log_download_progress)


def log_download_progress(num_bytes, obj_size):
    """Callback that boto can use to log download or upload progress"""
    logging.info('%s bytes transferred out of %s total', num_bytes, obj_size)


def list_files(s3_conn, s3_path):
    bucket_name, prefix = split_s3_path(s3_path)
    bucket = s3_conn.get_bucket(bucket_name)
    key = boto.s3.key.Key(
        bucket=bucket,
        name=prefix
    )
    files = []
    for key in bucket.list(prefix=prefix):
        files.append(key.name.split('/')[-1])
    return list(filter(None, files))
