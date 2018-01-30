# -*- coding: utf8 -*-
import os
import shutil
import errno
import re
import datetime
import six
import hashlib


try:
    from os import scandir, walk
except ImportError:
    from scandir import scandir, walk

try:
    from xattr import xattr as ExtendedFileAttributes
    has_xattr_support = True
except ImportError:
    has_xattr_support = False
    ExtendedFileAttributes = None


ignore_files = ['.DS_Store']


def __file_info_hash(sys, etag_or_filename):
    sha_1 = hashlib.sha1()

    if sys == 'local':
        with open(etag_or_filename, 'rb') as f:
            sha_1.update(f.read())
    else:
        etag = etag_or_filename.encode('ascii')
        sha_1.update(etag)

    return sha_1.hexdigest()


def __s3_info_to_file_info(item, fields=None):
    params = {
        'path': item['Key'],
        'sys': 's3',
    }

    if fields is None or 'size' in fields:
        params['size'] = item['Size']

    etag = item['ETag'].replace('"', '')

    if fields is None or 'etag' in fields:
        params['etag'] = etag

    if fields is None or 'mtime' in fields:
        params['mtime'] = item['LastModified'].replace(tzinfo=None)

    if fields is None or 'sha' in fields:
        params['sha'] = __file_info_hash(params['sys'], etag)

    return params


def __create_s3_paginator(**kwargs):
    import boto3

    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')

    return paginator.paginate(**kwargs)


def __split_bucket_prefix(bucket):
    try:
        bucket, prefix = bucket.split('/', 1)
    except ValueError:
        bucket, prefix = bucket, None

    return bucket, prefix


def __enumerate_path_s3(bucket, fields=None):
    bucket = remove_moniker(bucket)

    bucket, prefix = __split_bucket_prefix(bucket)

    for page in __create_s3_paginator(Bucket=bucket, Prefix=prefix):
        for item in page.get('Contents', []):
            if item['Key'].endswith('/'):  # skip folders
                continue

            yield __s3_info_to_file_info(item, fields)


def bucket_print_name(path):
    import boto3
    from botocore.exceptions import ClientError

    if path.startswith(s3_moniker):
        path = remove_moniker(path)
        bucket_name = path.split('/')[0]

        try:
            client = boto3.client('s3')

            response = client.get_bucket_location(Bucket=bucket_name)

            location = response.get('LocationConstraint') or 'us-east-1'
            return '%s (%s)' % (path, location)
        except ClientError:
            pass

    return path


def __get_xattr(attr):
    if not attr:
        return None, None

    try:
        data = attr.get('ai.ml.sha')
        data = data.decode()
        data = data.split('|')
        data[0] = float(data[0])
    except IOError as ex:
        data = (None, None)

    return data


def __set_xattr(attr, mtime, sha):
    global has_xattr_support

    if not attr:
        return

    data_encoded = '%s|%s' % (mtime, sha)
    data_encoded = data_encoded.encode()
    try:
        attr.set('ai.ml.sha', data_encoded)
    except IOError as ex:
        if ex.errno == 95:
            has_xattr_support = False
            return

        raise


def __file_to_info(path, st, fields):
    attr = ExtendedFileAttributes(path) if has_xattr_support else None

    params = {
        'path': path,
        'sys': 'local',
        'mtime': datetime.datetime.fromtimestamp(st.st_mtime),
        'ctime': datetime.datetime.fromtimestamp(st.st_ctime),
        'size': st.st_size,
        'mode': st.st_mode
    }

    if fields is None or 'sha' in fields:
        attr_mtime, attr_sha = __get_xattr(attr)

        if attr_mtime != st.st_mtime:
            params['sha'] = __file_info_hash(params['sys'], path)
            __set_xattr(attr, st.st_mtime, params['sha'])
        else:
            params['sha'] = attr_sha

    return params


def __file_name_to_info(filename, fields=None):
    return __file_to_info(filename, os.stat(filename), fields)


def __file_entry_to_info(entry, fields=None):
    return __file_to_info(entry.path, entry.stat(), fields)


def __recursive_scan(current_path, fields):
    try:
        for entry in scandir(current_path):
            if entry.is_dir():
                for info in __recursive_scan(entry.path, fields):
                    yield info

                continue

            yield __file_entry_to_info(entry, fields)
    except OSError as ex:
        if ex.errno == 20:
            yield __file_name_to_info(current_path, fields)
            return

        raise


def __enumerate_path_local(path, fields=None):
    for info in __recursive_scan(path, fields):
        yield info


s3_moniker = 's3://'


def enumerate_path_with_info(path, fields=None):
    if path.startswith(s3_moniker):
        enumerate_method = __enumerate_path_s3
    else:
        enumerate_method = __enumerate_path_local

    for file_info in enumerate_method(path, fields):
        full_object_name = file_info['path']
        file_name = os.path.basename(full_object_name)

        if file_name in ignore_files:
            continue

        yield file_info


def enumerate_paths_with_info(paths, fields=None):
    if isinstance(paths, six.string_types):
        paths = [paths]

    for path in paths:
        for file_info in enumerate_path_with_info(path, fields=fields):
            yield file_info


def enumerate_paths(paths):
    for file_info in enumerate_paths_with_info(paths, fields=['size']):
        yield file_info['path']


def get_total_files_in_path(paths, callback=None):
    total_files = 0

    for file_name in enumerate_paths(paths):
        count_file = True
        if callback is not None:
            count_file = callback(file_name)

        if count_file:
            total_files += 1

    return total_files


def is_glob(path):
    return '*' in path or '?' in path


def has_var(path):
    return '$' in path


def __validate_path_if_needed(path, validate_path):
    if not is_glob(path) and validate_path and not os.path.exists(path):
        raise IOError()


def __unslash(path):
    if path.endswith(os.sep):
        path = os.path.join(path, '')

    return path


def expend_and_validate_path(path, expand_vars=True, validate_path=True, abs_path=True):
    if path is None:
        return path

    result_path = path

    if expand_vars:
        result_path = os.path.expandvars(result_path)

    if has_moniker(path):
        return result_path

    result_path = os.path.expanduser(result_path)

    if abs_path:
        result_path = os.path.abspath(result_path)

    __validate_path_if_needed(result_path, validate_path)

    result_path = __unslash(result_path)

    return result_path


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_batch_of_files_from_paths(file_names, batch_size):
    for batch in chunks(file_names, batch_size):
        yield batch


def safe_make_dirs(dir_name):
    try:
        os.makedirs(dir_name)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def path_elements(path):
    if path.endswith(os.sep):
        path = path[:-1]

    folders = []
    while True:
        path, folder = os.path.split(path)

        if len(folder) > 0:
            folders.append(folder)
            continue

        if len(path) > 0:
            folders.append(path)

        break

    folders.reverse()

    return folders


def safe_rm_tree(path):
    try:
        shutil.rmtree(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise


class DestPathEnum(object):
    @classmethod
    def find_root(cls, dest):
        elements = path_elements(dest)

        root = []
        for element in elements:
            if has_var(element):
                break

            root.append(element)

        return os.path.join(*root)

    @classmethod
    def get_path_vars(cls, pattern, path):
        if path is None:
            return {}

        path_no_ext, file_extension = os.path.splitext(path)

        # in case the user has already specify '.' in the ext don't use dot in the var
        if '.$ext' in pattern or '.$@ext' in pattern:
            file_extension = file_extension[1:]

        return {
            'name': os.path.basename(path),
            'dir': os.path.dirname(path),
            'base_name': os.path.basename(path_no_ext),
            'ext': file_extension,
            'extension': file_extension
        }

    @classmethod
    def ___add_sys_var(cls, name, value, current_vars):
        current_vars['@' + name] = value

        if name not in current_vars:
            current_vars[name] = value

    @classmethod
    def __fill_in_vars(cls, path, replace_vars):
        replace_vars_keys = sorted(replace_vars.keys(), reverse=True)

        for var_name in replace_vars_keys:
            var_value = replace_vars[var_name]
            path = path.replace('$' + var_name, str(var_value))
            path = path.replace('#' + var_name, str(var_value))

        return path

    @classmethod
    def get_full_path(cls, dest, item):
        for key, val in cls.get_path_vars(dest, item.get('@path')).items():
            cls.___add_sys_var(key, val, item)

        phase = item.get('@phase')
        cls.___add_sys_var('phase', phase, item)
        item['@'] = phase

        dest_file = cls.__fill_in_vars(dest, item)

        return dest_file

    @classmethod
    def get_dest_path(cls, dest_folder, dest_file):
        if not dest_file:
            dest_file = '$@name'

        return os.path.join(dest_folder, dest_file)


def create_dir(dirname):
    if not dirname or os.path.exists(dirname):
        return

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def remove_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except (OSError, IOError):
        pass


def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))


def flatten_dir(root_dir):
    root_walk = os.walk(root_dir)
    _, top_level_dirs, _ = next(root_walk)

    for dirpath, _, filenames in root_walk:
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            shutil.move(filepath, root_dir)

    for top_level_dir in top_level_dirs:
        remove_dir(os.path.join(root_dir, top_level_dir))


def has_moniker(name):
    return '://' in name


def remove_moniker(name):
    try:
        index = name.index('://')
        return name[index + 3:]
    except ValueError:
        return name
