# -*- coding: utf8 -*-
import os
import shutil
import errno
import tempfile as tmp
from contextlib import contextmanager


def create_dir(dirname):
    if not dirname or os.path.exists(dirname):
        return

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def safe_make_dirs(dir):
    try:
        os.makedirs(dir)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def safe_rm_tree(path):
    try:
        shutil.rmtree(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise


@contextmanager
def tempfile(suffix='', dir_name=None):
    def remove():
        try:
            os.remove(tf.name)
        except OSError as e:
            if e.errno != 2:
                raise

    tf = tmp.NamedTemporaryFile(delete=False, suffix=suffix, dir=dir_name)
    tf.file.close()
    try:
        yield tf.name
    finally:
        remove()


@contextmanager
def open_atomic(file_path, *args, **kwargs):
    fsync = kwargs.get('fsync', False)

    with tempfile(dir_name=os.path.dirname(os.path.abspath(file_path))) as tmp_path:
        with open(tmp_path, *args, **kwargs) as file_:
            try:
                yield file_
            finally:
                if fsync:
                    file_.flush()
                    os.fsync(file_.fileno())

        os.rename(tmp_path, file_path)
