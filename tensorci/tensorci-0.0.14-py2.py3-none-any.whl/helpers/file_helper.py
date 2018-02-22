"""
Helper methods related to files or their respective paths
"""
import os


def path_to_components(path):
  """
  Split a file path into it's respective components:
    - Directory
    - Filename
    - File extension

  :param str path: File path
  :return: Components of file path: directory, filename, and file extension, respectively.
  :rtype: tuple(str, str, str)
  """
  comps = path.split('/')
  filename_with_ext = comps.pop()
  direc = '/'.join(comps) or None

  if '.' in filename_with_ext:
    file_comps = filename_with_ext.split('.')
    ext = file_comps.pop()
    filename = '.'.join(file_comps)
  else:
    ext = None
    filename = filename_with_ext

  return direc, filename, ext


def add_ext(filename, ext):
  """
  Add an extension to a filename if the extension exists

  :param str filename: Name of the file
  :param str ext: Potential extension of the file
  :return: Filename + extension
  :rtype: str
  """
  if not ext:
    return filename

  return '{}.{}'.format(filename, ext)


def filenames_with_ext(direc, ext):
  """
  For a given directory, return a map of all filenames with a given extension.

  :param str direc: The directory to list files for
  :param str ext: The extension to look for
  :return: A map of all filenames with the given extension
  :rtype: dict
  """
  if not ext:
    return {}

  return {n: True for n in os.listdir(direc) if n.endswith('.{}'.format(ext))}