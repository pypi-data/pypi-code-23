import os


def list_files(path, recursive=False):
    """List of the absolute path of all files within a folder.
    
    Args:
        path (str): The folder to be scanned for files.
        recursive (bool, optional): Defaults to False. Whether or not to include all subdirectories.
    
    Yields:
        str: The next file's absolute path within the folder
    """

    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            if dirnames and recursive:
                for d in dirnames:
                    list_files(os.path.join(dirpath, d))
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))
