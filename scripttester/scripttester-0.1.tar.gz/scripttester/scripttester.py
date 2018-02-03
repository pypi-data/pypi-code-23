""" Module to help tests check script output

Provides class to be instantiated in tests that check that scripts can be run
and give correct output.  Usually works something like this in a test module::

    import mymodule
    from scripttester import ScriptTester
    runner = ScriptTester(mymodule)

Then, in the tests, something like::

    code, stdout, stderr = runner.run_command(['my-script', my_arg])
    assert code == 0
    assert stdout == b'This script ran OK'

The class aims to find your scripts whether you have installed (with ``pip
install .`` or ``pip install -e .`` or ``python setup.py install``), or not.
If you have not installed, the scripts will not be on your system PATH, and we
have to find them.  The heuristic is to look (by default) in the directory
containing ``mymodule``; if there is a ``setup.py`` file there, and a
``scripts`` sub-directory, assume that directory contains the scripts.

Note there is no way of using this not-installed mechanism to find entrypoint
scripts, that have not been installed. To find these, we would have to run the
``setup.py`` file.
"""

import sys
import os
from os.path import (dirname, join as pjoin, isfile, isdir, realpath, pathsep)
from types import ModuleType
from importlib import import_module

from subprocess import Popen, PIPE

try: # Python 2
    string_types = basestring,
except NameError: # Python 3
    string_types = str,


class ScriptTester(object):
    """ Class to run scripts and return output

    Finds local scripts and local modules if running in the development
    directory, otherwise finds system scripts and modules.
    """
    def __init__(self,
                 module_or_name,
                 script_sdir='scripts',
                 filename_means_containing='setup.py',
                 debug_print_var=None,
                 output_processor=lambda x : x,
                 win_bin_ext='.exe',
                ):
        """ Initialise ScriptTester instance

        Parameters
        ----------
        module_or_name : module or str
            Package module, or name of package, in which to find scripts.
        script_sdir : str, optional
            Name of subdirectory in top-level directory (directory containing
            file named in `filename_means_containing`), to find scripts in
            development tree.  Typically this is 'scripts', but might be 'bin'
            or something else.
        filename_means_containing : str, optional
            Filename (without path) that, if present in the directory
            containing `module`, indicates this is the development directory.
        debug_print_var : str, optional
            Name of environment variable that indicates whether to do debug
            printing or no.
        output_processor : callable, optional
            Callable to run on the stdout, stderr outputs before returning
            them.  Use this to convert bytes to unicode, strip whitespace, etc.
        win_bin_ext : str, optional
            Extension to indicate callable binary on Windows.  Usually ``.exe``
            (for setuptools installs), but can be ``.bat`` (for my .bat file
            solution at [1]).

        Notes
        -----
        [1] https://matthew-brett.github.io/pydagogue/installing_scripts.html
        """
        module = (module_or_name if isinstance(module_or_name, ModuleType)
                  else import_module(module_or_name))
        self.module = module
        self.script_sdir = script_sdir
        self.filename_means_containing = filename_means_containing
        if debug_print_var is None:
            debug_print_var = '{0}_DEBUG_PRINT'.format(
                self.module_path.upper())
        self.debug_print = os.environ.get(debug_print_var, False)
        self.output_processor = output_processor
        self.win_bin_ext = win_bin_ext
        self.local_script_dir = self.devel_script_dir()
        self.local_module_dir = self.devel_dir_if_cwd()

    @property
    def module_path(self):
        return realpath(dirname(self.module.__file__))

    def devel_script_dir(self):
        """ Get local script directory if module appears to be running in dev tree.

        Returns
        -------
        dev_script_dir : None or str
            Path string to local scripts directory if directory containing module
            has a file called ``setup.py`` (by default), and there is a subdirectory with name
            given in `script_dir`, None otherwise.  In fact we check for a file
            named ``self.filename_means_containing``, set to ``setup.py`` by
            default.
        """
        # Check for presence of scripts in development directory.  ``realpath``
        # allows for the situation where the development directory has been linked
        # into the path.
        above_us = realpath(pjoin(self.module_path, '..'))
        dev_script_dir = pjoin(above_us, self.script_sdir)
        if (isfile(pjoin(above_us, self.filename_means_containing))
            and isdir(dev_script_dir)):
            return dev_script_dir
        return None

    def devel_dir_if_cwd(self):
        """ Get module directory if it is the working directory, else None

        Returns
        -------
        dir_or_none : None or str
            Path string to directory containing `module` if this is also the
            current working directory, None otherwise.
        """
        containing_path = dirname(self.module_path)
        if containing_path == realpath(os.getcwd()):
            return containing_path
        return None

    def run_command(self, cmd, check_code=True):
        """ Run command sequence `cmd` returning exit code, stdout, stderr

        Parameters
        ----------
        cmd : str or sequence
            string with command name or sequence of strings defining command
        check_code : {True, False}, optional
            If True, raise error for non-zero return code

        Returns
        -------
        returncode : int
            return code from execution of `cmd`
        stdout : bytes (python 3) or str (python 2)
            stdout from `cmd`
        stderr : bytes (python 3) or str (python 2)
            stderr from `cmd`
        """
        cmd = [cmd] if isinstance(cmd, string_types) else list(cmd)
        using_sys_path = self.local_script_dir is None
        if not using_sys_path:
            # Windows can't run script files without extensions natively so we need
            # to run local scripts (no extensions) via the Python interpreter.  On
            # Unix, we might have the wrong incantation for the Python interpreter
            # in the hash bang first line in the source file.  So, either way, run
            # the script through the Python interpreter
            cmd = [sys.executable,
                   pjoin(self.local_script_dir, cmd[0])] + cmd[1:]
        elif os.name == 'nt':
            # Must add extension to find on path with Windows
            cmd[0] = cmd[0] + self.win_bin_ext
        if os.name == 'nt':
            # Quote any arguments with spaces. The quotes delimit the arguments
            # on Windows, and the arguments might be file paths with spaces.
            # On Unix the list elements are each separate arguments.
            cmd = ['"{0}"'.format(c) if ' ' in c else c for c in cmd]
        if self.debug_print:
            print("Running command '%s'" % cmd)
        env = os.environ
        if using_sys_path and self.local_module_dir:
            # module likely comes from the current working directory. We might
            # need that directory on the path if we're running the scripts from
            # a temporary directory.
            env = env.copy()  # Modifying env, make temporary copy.
            pypath = env.get('PYTHONPATH', None)
            if pypath is None:
                env['PYTHONPATH'] = self.local_module_dir
            else:
                env['PYTHONPATH'] = self.local_module_dir + pathsep + pypath
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env)
        stdout, stderr = proc.communicate()
        if proc.poll() == None:
            proc.terminate()
        if check_code and proc.returncode != 0:
            raise RuntimeError(
                """Command "{0}" failed with
                stdout
                ------
                {1}
                stderr
                ------
                {2}
                """.format(cmd, stdout, stderr))
        opp = self.output_processor
        return proc.returncode, opp(stdout), opp(stderr)
