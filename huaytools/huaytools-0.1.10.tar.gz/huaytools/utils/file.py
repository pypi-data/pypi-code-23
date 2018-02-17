"""文件相关

"""
from __future__ import print_function

import os
from huaytools import maybe_mkdirs
from six.moves import urllib

# __all__ = [
#     'maybe_download',
#     'rename_replace_sep',
#     'rename_batch',
#     'get_dir_filenames'
# ]


def maybe_download(url, to_path='D:/Tmp', filename=None, expected_byte=None):
    """下载文件到指定目录

    Args:
        url (str): 文件下载路径
        to_path (str): 下载到本地路径
        filename (str): 重命名文件
        expected_byte (int): 文件预期大小

    Returns:
        str: filepath

    Examples:

        >>> url = 'http://mattmahoney.net/dc/bbb.zip'
        >>> filepath = maybe_download(url, filename='b.zip')
        File is ready.
        >>> fp = maybe_download(url, to_path='D:/Tmp/b', expected_byte=45370)
        File is downloading.
        File has been damage, please download it manually.

    """
    if filename is not None:
        filepath = os.path.join(maybe_mkdirs(to_path), filename)
    else:
        _, filename = os.path.split(url)
        filepath = os.path.join(maybe_mkdirs(to_path), filename)

    if not os.path.exists(filepath):
        urllib.request.urlretrieve(url, filepath)
        print('File is downloading.')

        if expected_byte is not None:
            file_size = os.stat(filepath).st_size
            if file_size != expected_byte:
                print('File has been damage, please download it manually.')
    else:
        print('File is ready.')

    return filepath


def rename_replace_sep(filename, new_sep='_', prefix=None, lower_case=False, sep=None, maxsplit=-1):
    """重命名：替换分隔符

    Args:
        filename (str): 原文件名，不包含路径
        new_sep (str): 新分隔符，默认是 '_'
        prefix (str): 前缀，分隔符会自动添加
        lower_case (bool): 是否替换成小写
        sep (str): 需要替换的分隔符，默认是所有空白符
        maxsplit (int): 分割几段，-1 表示全部分割

    Returns:
        str

    Examples：

        >>> rename_replace_sep('a b c.txt', prefix='M')
        'M_a_b_c.txt'

    """
    if lower_case:
        filename.lower()
    if prefix is not None:
        filename = new_sep.join([prefix, filename])
    return new_sep.join(filename.split(sep, maxsplit))


def get_dir_filenames(dirpath, abspath=True, recursive=True, yield_=True):
    """获取目录下所有文件名 （默认递归）

    该函数仅用于需要一次性处理大量**同类文件**的情况

    又发现一个实用的库函数
        root, dirs, files = os.walk(path)
    该函数会递归遍历 path 下的所有文件夹

    注意：一旦函数体中出现 yield from 关键字，该函数就会被认为是一个生成器函数，
    无论该 yield from 语句是否被执行；
    因此，额外定义了两个函数 `_get_dir_filenames_list` 和 `_get_dir_filenames_yield`

    Args:
        dirpath (str): 文件夹路径
        abspath (bool): 是否返回绝对路径
        recursive (bool): 是否递归
        yield_ (bool): 是否使用生成器模式，实测确实可以"加速"

    Examples:

        >>> fs_list = get_dir_filenames('D:/Tmp', yield_=False)
        >>> fs_gen = get_dir_filenames('D:/Tmp')

        %timeit hy.get_dir_filenames('D:/Tmp', yield_=False)
        182 ms ± 1.13 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

        %timeit hy.get_dir_filenames('D:/Tmp')
        391 ns ± 1.69 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

    """
    if yield_:
        return _get_dir_filenames_yield(dirpath, abspath=abspath, recursive=recursive)
    else:
        return _get_dir_filenames_list(dirpath, abspath=abspath, recursive=recursive)


def _get_dir_filenames_list(dirpath, abspath=True, recursive=True):
    """获取目录下所有文件名 （返回列表）

    参数含义同 `get_dir_filenames()`

    """
    fs = []
    if recursive:
        for root, _, files in os.walk(dirpath):
            if abspath:
                fs.extend((os.path.join(root, file) for file in files))
            else:
                fs.extend(files)
    else:
        if abspath:
            fs.extend((os.path.join(dirpath, file) for file in os.listdir(dirpath)))
        else:
            fs.extend(os.listdir(dirpath))

    return fs


def _get_dir_filenames_yield(dirpath, abspath=True, recursive=True):
    """get_dir_filenames() 的生成器版本

    参数含义同 `get_dir_filenames()`

    """
    # if recursive:
    #     for root, _, files in os.walk(dirpath):
    #         if abspath:
    #             yield from (os.path.join(root, file) for file in files)
    #         else:
    #             yield from (file for file in files)
    # else:
    #     if abspath:
    #         yield from (os.path.join(dirpath, file) for file in os.listdir(dirpath))
    #     else:
    #         yield from (file for file in os.listdir(dirpath))

    yield from _get_dir_filenames_list(dirpath, abspath=abspath, recursive=recursive)


def rename_batch(dirpath, rename_fn=rename_replace_sep, recursive=True):
    """文件批量重命名

    默认行为是将文件名中的空白符替换成 '_'

    Args:
        dirpath (str): 文件目录
        rename_fn (callable): 重命名方法
        recursive (bool): 是否递归

    Examples:

        >>> rename_batch('D:\Tmp')

    """
    fs = get_dir_filenames(dirpath, recursive=recursive)
    for f in fs:
        path, filename = os.path.split(f)
        new = rename_fn(filename)
        os.rename(f, os.path.join(path, new))


def rename_del_ext(filename):
    """重命名：删除后缀"""
    filename, _ = os.path.splitext(filename)
    return filename
