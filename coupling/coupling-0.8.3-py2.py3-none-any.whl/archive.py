# -*- coding: utf-8 -*-

import os
import zipfile
import tarfile
from . import fs

import logging
logger = logging.getLogger(__name__)


class Type(object):
    ZIP = 1
    TGZ = 2
    TBZ = 3


def extract(path, dest=None, members=None):
    if dest is None:
        dest = os.path.dirname(path)

    logger.info("extract: path=[%s], dest=[%s]", path, dest)

    if tarfile.is_tarfile(path):
        tar_obj = tarfile.open(path)
        tar_obj.extractall(dest)
        tar_obj.close()
    elif zipfile.is_zipfile(path):
        zip_obj = zipfile.ZipFile(path)
        if members is None:
            zip_obj.extractall(dest)
        else:
            for member in members:
                zip_obj.extract(member, dest)
        zip_obj.close()
    else:
        raise ValueError("unsupported archive type")


def archive(src, path, exclude=None, type=Type.ZIP):
    logger.info("archive: src=[%s], path=[%s], exclude=[%s], type=[%s]", src, path, exclude, type)

    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        fs.mkdirs(dir_path)

    if type == Type.ZIP:
        zip_obj = zipfile.ZipFile(path, "w")
        if os.path.isdir(src):
            for found in fs.find(src, exclude=exclude):
                logger.debug("found: %s", found)
                rel_name = os.path.relpath(found, src)
                if rel_name != ".":
                    rel_name = rel_name.replace("\\", "/")
                    if os.path.isdir(found):
                        rel_name += "/"
                    zip_obj.write(found, rel_name)
        else:
            zip_obj.write(src, os.path.basename(src))
        zip_obj.close()
    elif type == Type.TGZ or type == Type.TBZ:
        raise NotImplementedError
    else:
        raise ValueError("unsupported archive type")
