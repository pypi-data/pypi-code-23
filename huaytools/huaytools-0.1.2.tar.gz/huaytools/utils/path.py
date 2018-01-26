import os

def maybe_mkdirs(dirs, exist_ok=True):
    """创建文件夹
    即使文件夹已经存在


    """
    os.makedirs(dirs, exist_ok=exist_ok)