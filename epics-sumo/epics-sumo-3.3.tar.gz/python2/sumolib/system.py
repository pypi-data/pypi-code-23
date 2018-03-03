"""System utilities.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import subprocess

__version__="3.3" #VERSION#

# -----------------------------------------------
# basic system utilities
# -----------------------------------------------

def system_rc(cmd, catch_stdout, catch_stderr, verbose, dry_run):
    """execute a command.

    execute a command and return the programs output
    may raise:
    IOError(errcode,stderr)
    OSError(errno,strerr)
    ValueError
    """
    if dry_run or verbose:
        print ">", cmd
        if dry_run:
            return (None, None, 0)
    if catch_stdout:
        stdout_par=subprocess.PIPE
    else:
        stdout_par=None

    if catch_stderr:
        stderr_par=subprocess.PIPE
    else:
        stderr_par=None

    p= subprocess.Popen(cmd, shell=True,
                        stdout=stdout_par, stderr=stderr_par,
                        close_fds=True)
    (child_stdout, child_stderr) = p.communicate()
    # pylint: disable=E1101
    #         "Instance 'Popen'has no 'returncode' member
    return (child_stdout, child_stderr, p.returncode)

def system(cmd, catch_stdout, catch_stderr, verbose, dry_run):
    """execute a command with returncode.

    execute a command and return the programs output
    may raise:
    IOError(errcode,stderr)
    OSError(errno,strerr)
    ValueError
    """
    (child_stdout, child_stderr, rc)= system_rc(
                                            cmd,
                                            catch_stdout, catch_stderr,
                                            verbose, dry_run)
    if rc!=0:
        if catch_stderr:
            raise IOError(rc,
                          "cmd \"%s\", errmsg \"%s\"" % (cmd,child_stderr))
        else:
            raise IOError(rc,
                          "cmd \"%s\", rc %d" % (cmd, rc))
    return (child_stdout, child_stderr)

program_tests= set()

def test_program(cmd):
    """test if a program exists."""
    if cmd in program_tests:
        # already checked
        return
    try:
        system(cmd+" --version", True, True, False, False)
    except IOError, e:
        if "not found" in str(e):
            raise IOError("Error, %s: command not found" % cmd)
        raise e
    program_tests.add(cmd)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
