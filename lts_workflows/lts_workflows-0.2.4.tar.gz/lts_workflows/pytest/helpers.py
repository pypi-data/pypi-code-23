# -*- coding: utf-8 -*-
import os
import sys
import pytest
import subprocess as sp
import contextlib

SNAKEMAKE_LAYOUTS = {
    "sample": {'runfmt': '{SM}/{SM}_{PU}', 'samplefmt': '{SM}/{SM}'},
    "sample_run":  {'runfmt': '{SM}/{PU}/{SM}_{PU}', 'samplefmt': '{SM}/{SM}'},
    "sample_project_run":  {'runfmt': '{SM}/{BATCH}/{PU}/{SM}_{PU}',
                            'samplefmt': '{SM}/{SM}'},
    "pop_sample": {'runfmt': '{POP}/{SM}/{SM}_{PU}',
                   'samplefmt': '{POP}/{SM}/{SM}'},
    "pop_sample_run":  {'runfmt': '{POP}/{SM}/{PU}/{SM}_{PU}',
                        'samplefmt': '{POP}/{SM}/{SM}'},
    "pop_sample_project_run": {'runfmt': '{POP}/{SM}/{BATCH}/{PU}/{SM}_{PU}',
                               'samplefmt': '{POP}/{SM}/{SM}'},
}


# Helper function to make output executable
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


def run(cmd, env=None, stdout=sp.PIPE, stderr=sp.STDOUT):
    """Run workflow subprocess.

    NB: setting env argument to Popen doesn't seem to work; presumably
    the source command wipes env clean

    Args:
      cmd (str): command to run
      env (str): conda environment to activate
    """
    close_fds = sys.platform != 'win32'

    env_prefix = "source activate {};".format(env) if env else ""
    proc_prefix = "set -euo pipefail;"
    if env:
        path = ":".join([os.path.join(p, "bin")
                         for (n, p, env) in pytest.conda_env_list])
        prepend_path = "PATH=\"{}:$PATH\"".format(path)
    else:
        prepend_path = ""
    proc = sp.Popen("{} {} {} {}".format(
        env_prefix,
        proc_prefix,
        prepend_path,
        cmd),
                    bufsize=-1,
                    shell=True,
                    stdout=stdout,
                    stderr=stderr,
                    close_fds=close_fds,
                    executable="/bin/bash")
    output, err = proc.communicate()
    return output, err


def snakemake_list(snakemakedata, results, env=None, **kwargs):
    """Run snakemake list"""

    d = snakemakedata
    cmd = " ".join(['snakemake', '-l', '-d', str(d), '-s',
                    str(d.join("Snakefile"))])
    output, err = run(cmd, env, sp.PIPE, sp.STDOUT)
    print("\n", output.decode("utf-8"))
    assert(output.decode("utf-8").find(results) > -1)


def snakemake_run(d, env=None, **kwargs):
    """Run snakemake workflow"""
    options = kwargs.get("options", ["--ri", "-k"])
    options += ['-j', str(kwargs.get("threads", "1")), '-d', str(d),
                '-s', str(d.join("Snakefile"))]
    if kwargs.get("use_conda", False):
        options = options + ["--use-conda"]
    if kwargs.get("config", False):
        options = options + ["--configfile", kwargs.get('config')]
    cmd = " ".join(['snakemake'] + options + [kwargs.get('target', 'all')])
    cmdfile = os.path.join(str(d), "command.sh")
    with open(cmdfile, "w") as fh:
        fh.write("#!/bin/bash\n")
        fh.write("PATH={}\n".format(os.environ["PATH"]))
        fh.write("args=$*\n")
        fh.write(cmd + " ${args}\n")
    make_executable(cmdfile)

    output, err = run(cmd, env,
                      kwargs.get("stdout", None),
                      kwargs.get("stderr", None))
    # Rerun to get assert statement
    cmd = " ".join(['snakemake'] + options + ['-n'] +
                   [kwargs.get('target', 'all')])
    output, err = run(cmd, env)
    assert (output.decode("utf-8").find(
        kwargs.get("results", "Nothing to be done")) > -1)


# context manager for cd
@contextlib.contextmanager
def cd(path):
    CWD = os.getcwd()
    print("Changing directory from {} to {}".format(CWD, path),
          file=sys.stderr)

    os.chdir(path)
    try:
        yield
    except:
        print('Exception caught: ', sys.exc_info()[0], file=sys.stderr)
    finally:
        print("Changing directory back to {}".format(CWD), file=sys.stderr)
        os.chdir(CWD)
