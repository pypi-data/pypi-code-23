# -*- coding: utf-8 -*-

import os
import tarfile


def tar_files(file_path_list, tar_file_path, gzip=True):
    """将文件列表打进 tar 包

    Args:
        file_path_list  : 文件/目录 列表
        tar_file_path   : tar 包文件路径
        gzip            : 是否进行 gzip 压缩         

    Returns:
        err(Exception): 返回错误，None 表示正常
    """
    try:
        mode = "w:gz" if gzip else "w"
        tar = tarfile.open(tar_file_path, mode)
        for file_path in file_path_list:
            fname = os.path.basename(file_path)
            tar.add(file_path, arcname=fname)
        tar.close()
    except Exception as err:
        return err
    return None


def untar_file(tar_file, outout_base_dir, gzip=True):
    """将 tar 包解压到目录

    Args:
        tar_file        : tar 包路径
        output_base_dir : 解压的根目录
        gzip            : 是否进行 gzip 解压      

    Returns:
        err(Exception): 返回错误，None 表示正常
    """
    try:
        mode = "r:gz" if gzip else "r"
        tar = tarfile.open(tar_file, mode)
        tar.extractall(path=outout_base_dir)
        tar.close()
    except Exception as err:
        return err
    return None
