"""tar file support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os.path
import shutil
import sumolib.system
import sumolib.utils
import sumolib.fileurl

__version__="3.3" #VERSION#

assert __version__==sumolib.system.__version__
assert __version__==sumolib.utils.__version__
assert __version__==sumolib.fileurl.__version__

# -----------------------------------------------
# Repo class
# -----------------------------------------------

class Repo(object):
    """represent a tar."""
    def _hint(self, name):
        """return the value of hint "name"."""
        return self.hints.get(name)
    @staticmethod
    def _find_tar(directory):
        """look for a tar file for <directory>.

        If directory is "a/b/c" look for:
          a/b/c.tar
          a/b/c.tar.gz
          a/b/c.tar.bz
          a/b-c.tar
          a/b-c.tar.gz
          a/b-c.tar.bz
        """
        def find(directory):
            """try to find the tar file."""
            for ext in [".tar",".tar.gz",".tar.bz"]:
                f= directory+ext
                if os.path.exists(f):
                    return f
            return
        abs_directory= os.path.abspath(directory)
        (d,base)= os.path.split(abs_directory)
        (dir_,parent)= os.path.split(d)
        paths= [abs_directory,
                os.path.join(dir_,"%s-%s" % (parent,base)),
               ]
        for p in paths:
            result= find(p)
            if result is not None:
                return result
        return
    def __init__(self, directory, tar_url, hints, verbose, dry_run):
        """initialize."""
        # pylint: disable=R0913
        #                          Too many arguments
        self.hints= dict(hints) # shallow copy
        patcher= self._hint("dir patcher")
        if patcher is not None:
            directory= patcher.apply(directory)
        patcher= self._hint("url patcher")
        if patcher is not None:
            tar_url= patcher.apply(tar_url)
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        self.tar_url= tar_url
    def __str__(self):
        """return a human readable representation."""
        lines= [ "tar file",
                 "dir: %s" % repr(self.directory),
                 "tar url: %s" % repr(self.tar_url)
               ]
        return "\n".join(lines)
    def name(self):
        """return the repo type name."""
        # pylint: disable=R0201
        #                          Method could be a function
        return "tar"
    @classmethod
    def scan_dir(cls, directory, hints, verbose, dry_run):
        """return a Repo object."""
        # pylint: disable=W0613
        #                          Unused argument
        tar_file= None
        # If directory is None we want to create an "empty" object
        # intentionally. In this case we don't look for a tar file.
        # If directory is given however, we must find a tar file. If we don't
        # we return <None>.
        if directory is not None:
            tar_file= cls._find_tar(directory)
            if tar_file is None:
                return
        return cls(directory, tar_file, hints, verbose, dry_run)
    def source_spec(self):
        """return a complete source specification (for SourceSpec class).
        """
        if self.directory is None:
            raise AssertionError("cannot create source_spec from "
                                 "empty object")
        d= {"type":"tar",
            "url" : self.tar_url
           }
        return d
    @staticmethod
    def checkout(spec, destdir, _, verbose, dry_run):
        """spec must be a dictionary with key "url".

        The tar file is placed in basename(destdir).
        """
        # pylint: disable=R0914
        #                          Too many local variables
        # pylint: disable=R0912
        #                          Too many branches
        def single_subdir(dir_):
            """If dir_ has a single subdir, return it."""
            contents= os.listdir(dir_)
            if len(contents)!=1:
                return
            subdir= os.path.join(dir_,contents[0])
            if os.path.isdir(subdir):
                return subdir
            return

        url       = spec["url"]
        ap_destdir= os.path.abspath(destdir)

        ap_file=  os.path.join(os.path.dirname(ap_destdir),
                               os.path.basename(url))

        ext= os.path.splitext(ap_file)[1]
        if ext==".tar":
            tar_args= "-xf"
        elif ext==".gz":
            tar_args= "-xzf"
        elif ext==".bz2":
            tar_args= "-xjf"
        else:
            raise ValueError("unknown file %s extension at %s" % \
                             (ext,url))

        # we must first fetch the file
        sumolib.fileurl.get(url, ap_file, verbose, dry_run)

        ap_tempdir= destdir+".tmp"
        os.makedirs(ap_tempdir)
        cwd= sumolib.utils.changedir(ap_tempdir)
        try:
            sumolib.system.system("tar %s %s" % (tar_args, ap_file),
                                  False, False, verbose, dry_run)
        finally:
            sumolib.utils.changedir(cwd)
        ap_subdir= single_subdir(ap_tempdir)
        if not ap_subdir:
            # The files lie directly in ap_tempdir:
            os.rename(ap_tempdir, ap_destdir)
            return
        # The tar file created a single directory within ap_tempdir so we have
        # to remove one directory hierarchy:
        ap_renamed_subdir= os.path.join(ap_tempdir, os.path.basename(destdir))
        os.rename(ap_subdir, ap_renamed_subdir)
        shutil.move(ap_renamed_subdir, ap_destdir)
        os.rmdir(ap_tempdir)
