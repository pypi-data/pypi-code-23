# find_tools.py

import os



def findfile(extension, path = ""):
    """
    Returns name of file with extension in current working directory

    Args:
        extension: Examples include ".txt", ".pcr", ".py" etc.

    Raises:
        No exception is raised for multiple files with file ending "extension".
        but comments are printed to the console about the nature of extension
        and how many additional files were found.

    """
    path = os.getcwd() if path == "" else path
    files = [f for f in os.listdir( path ) if f.endswith( extension )]
    searched_file = files[0] if len(files)==1 else "error!"
    if searched_file == "error!":
        print("error in folder:", path)
        print("number of files with extension", "\"" + extension + "\"", "is", len( files ))
    return searched_file

def findfile_abspath(extension, path = ""):
  """ returns only one file with extension """
  path = os.getcwd() if path == "" else path
  files = [os.path.join( path, f ) for f in os.listdir( path ) if f.endswith( extension )]
  searched_file = files[0] if len(files)==1 else "error!"
  if searched_file == "error!":
    print("error finding file with extension:", extension, "in folder", path )
    print("number of files with extension:", len( files ))
  return searched_file


def findfiles(extension, path = ""):
    """
    Returns all files with specified extension in the current working directory

    Args:
        extension: Examples include ".txt", ".pcr", ".py" etc.

    Returns:
        list of files with specified extension.

    """
    path = os.getcwd() if path == "" else path
    return [f for f in os.listdir( path ) if f.endswith( extension )]

def findfiles_abspath(extension, path = ""):
  """ returns all files with specified extension """
  path = os.getcwd() if path == "" else path
  return [os.path.join( path, f ) for f in os.listdir( path ) if f.endswith( extension )]


def findfolders(path = "" ):
    """
    Returns all folders in current working directory

    Returns:
        list of directories in current working directory

    """
    path = os.getcwd() if path == "" else path
    return [f for f in os.listdir( path ) if os.path.isdir( f )]

def findfolders_abspath( path = "" ):
  """ returns all folders in cwd """
  path = os.getcwd() if path == "" else path
  return [os.path.join( path, f ) for f in os.listdir( path ) if os.path.isdir( f )]
