"""
Helper methods related to files or their respective paths
"""
import os
import shutil
import zipfile
from tensorci import log


def create_model_save_path(path, download_ext):
  """
  Create path to save a model to.
  Validate the provided and desired extensions are compatible.

  :param str path: Desired model path (either filename or directory)
  :param str download_ext: File extension of downloaded model content
  :return: Path to save model to.
  :rtype: str
  """
  archive = 'zip'  # All model folders should be downloaded as zip files.

  # Check if the specified model path is a directory
  is_dir = path.endswith('/') or ('.' not in path.split('/').pop())

  # Ensure downloaded file is a zip file if model path is a directory
  if is_dir:
    if download_ext != archive:
      log('Can\'t download model -- Specified model path was a directory, '
          'but downloaded model not a {} file.'.format(archive))
      exit(1)

    save_to = '.'.join((path.rstrip('/'), archive))
  else:
    ext = path.split('/').pop().split('.').pop()

    # If model is a file (not a dir), ensure its ext matches the downloaded file ext.
    if ext != download_ext:
      log('Can\'t donwload model -- Expected type: {}; Actual type: {}'.format(ext, download_ext))
      exit(1)

    save_to = path

  return save_to


def upsert_parent_dirs(filepath):
  """
  Similar to os.makedirs, but ignores filename and doesn't raise an error when
  a directory is already in existence...it just skips it.

  :param str filepath: File path to upsert all parent directories for
  """
  comps = [c for c in filepath.split('/') if c]
  comps.pop()

  if filepath.startswith('/'):
    path = '/'
  else:
    path = ''

  for dir in comps:
    path += (dir + '/')

    if not os.path.exists(path):
      try:
        os.mkdir(path)
      except:
        pass


def extract_in_place(archive_path):
  """
  Unpack a zipfile in place and remove it upon completion.

  Ex:
    extract_in_place('path/to/archive.zip')
    # => creates 'path/to/archive/' directory

  :param str archive_path: Path to zipfile
  :return: Path to directory where zipfile contents were extracted
  :rtype: str
  """
  # Comments using values from example of archive_path='/path/to/model.zip
  filename_w_ext = archive_path.split('/').pop()        # model.zip
  ext = filename_w_ext.split('.').pop()                 # zip
  extract_dir = archive_path[:-(len(ext) + 1)]          # /path/to/model

  # Remove the destination dir if it already exists
  if os.path.exists(extract_dir) and os.path.isdir(extract_dir):
    shutil.rmtree(extract_dir)

  # Unpack the archive
  archive = zipfile.ZipFile(archive_path)
  archive.extractall(extract_dir)
  archive.close()

  # Remove the archive file
  os.remove(archive_path)

  return extract_dir
