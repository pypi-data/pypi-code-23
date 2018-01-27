import os


def maybe_mkdirs(dirs, exist_ok=True):
    """创建文件夹

    Args:
        dirs (str): 待创建的目录路径，支持地柜创建
        exist_ok (bool): 默认为 True

    Examples:

        >>> maybe_mkdirs('D:/Tmp/a/b/c')

    Returns:
        None

    """
    os.makedirs(dirs, exist_ok=exist_ok)