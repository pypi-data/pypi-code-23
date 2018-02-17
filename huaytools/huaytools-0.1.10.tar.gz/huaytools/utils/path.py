import os


def maybe_mkdirs(path, filepath=False, exist_ok=True):
    """（可能需要）创建文件夹

    如果 path 是一个文件夹路径，则直接创建
    如果 path 是一个包含文件名的路径，则忽略文件名，创建路径

    Args:
        path (str): 待创建的目录路径，递归创建
        filepath (bool): 如果 path 是一个文件路径，创建该文件依赖的目录
            设置该参数的目的主要是为了判断无后缀的文件，
            对于带后缀的文件会自动判断
        exist_ok (bool): 默认为 True

    Returns:
        str

    Examples:

        >>> maybe_mkdirs('D:/Tmp/a/b/')
        'D:/Tmp/a/b/'
        >>> maybe_mkdirs('D:/Tmp/a/b/c.txt')
        'D:/Tmp/a/b/c.txt'
        >>> maybe_mkdirs('D:/Tmp/a/b/c', filepath=True)  # c 是一个无后缀文件
        'D:/Tmp/a/b/c'

    """
    if filepath:
        dirs, filename = os.path.split(path)
        os.makedirs(dirs, exist_ok=exist_ok)
        return path

    if os.path.splitext(path)[1].startswith('.'):  # 是一个文件路径
        dirs, filename = os.path.split(path)
        os.makedirs(dirs, exist_ok=exist_ok)
    else:
        os.makedirs(path, exist_ok=exist_ok)

    return path
