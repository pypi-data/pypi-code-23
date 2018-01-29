import os


def break_file(path):
  comps = path.split('/')
  filename_with_ext = comps.pop()
  direc = '/'.join(comps)

  if not direc:
    direc = None

  if '.' in filename_with_ext:
    file_comps = filename_with_ext.split('.')
    ext = file_comps.pop()
    filename = '.'.join(file_comps)
  else:
    ext = None
    filename = filename_with_ext

  return direc, filename, ext


def add_ext(filename, ext):
  if ext:
    return '{}.{}'.format(filename, ext)

  return filename


def filenames_with_ext(direc, ext):
  if ext:
    return {n: True for n in os.listdir(direc) if n.endswith('.{}'.format(ext))}

  return {}