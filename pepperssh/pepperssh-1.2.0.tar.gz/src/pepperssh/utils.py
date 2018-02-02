
import os, zipfile, fnmatch, glob
import subprocess
from os.path import isabs, join, relpath
from contextlib import contextmanager


def shell(cmd, check=True):
    """
    Execute cmd.  Raises an exception if the command does not return 0
    """
    proc = subprocess.run(cmd, shell=True, check=False, stderr=subprocess.STDOUT,
                          stdout=subprocess.PIPE)
    output = proc.stdout.decode('utf-8').strip()
    if output:
        print(output)
    if check:
        proc.check_returncode()


def ensurelist(paramname, val, comment='#'):
    """
    Returns `val` as a list of strings.

    If `val` is already a list of strings, it is returned as-is.  If a string
    is passed, it is split into lines and blink and (optionally) comment lines
    are removed.

    paramname
      The parameter name to put into error messages.

    comment
      The single-line comment identifier.  Any lines starting with this are
      removed.  Note that end-of-line comments are *not* removed.
    """

    if isinstance(val, list):
        for line in val:
            if not isinstance(line, str):
                typename = type(line).__qualname__
                raise TypeError(f"{paramname} should be a list of strings.  Found: {typename}")
        return val

    if isinstance(val, str):
        lines = (line.strip() for line in val.strip().split('\n'))
        lines = (line for line in lines if line)
        if comment:
            lines = (line for line in lines if not line.startswith())
        return lines

    raise TypeError(f'{paramname} must be a list of strings or a string')


def archive(filename, *, include, root=None, exclude_files=None,
            nocompression=['*.png', '*.jpg']):
    """
    Creates a zip file.

    root
      An optional directory used as the parent of all relative paths in other
      parameters.  If not provided, the current working directory is used.

    include
      A list of glob patterns to be added.  For convenience a string can be
      passed which will be split on newlines, allowing a triple-quoted string
      to be used.

      Each pattern is treated as a recursive pattern.  To disable, end the
      pattern with '/*'0

    exclude_files
      A list of shell patterns to exclude, such as '*.log'.  The fnmatch
      package is used to compare.
    """
    if not root:
        root = os.getcwd()

    if isinstance(include, str):
        lines = (line.strip() for line in include.split('\n'))
        nonblank = (line for line in lines
                    if line and not line.startswith('#'))
        include = list(nonblank)

    archive = zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED)

    def _matches_pattern(fn, patterns):
        if not patterns:
            return False
        for pattern in patterns:
            if fnmatch.fnmatch(fn, pattern):
                return True
        return False

    for spec in include:
        if isabs(spec):
            raise ValueError(
                f'Include specifications cannot be absolute.  ({spec!r})'
            )
        spec = join(root, spec)
        recursive = not spec.endswith('/*')
        for fn in glob.iglob(spec, recursive=recursive):

            if _matches_pattern(fn, exclude_files):
                continue

            compression = None
            if _matches_pattern(fn, nocompression):
                compression = zipfile.ZIP_STORED

            arcname = relpath(fn, root)
            archive.write(fn, arcname, compress_type=compression)

    return filename


@contextmanager
def chdir(dir):
    prev = os.getcwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(prev)
