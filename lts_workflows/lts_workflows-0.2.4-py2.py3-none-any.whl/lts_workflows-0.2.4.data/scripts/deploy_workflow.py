#!python
import os
import re
import sys
import shutil
import argparse
import logging
import yaml
import ast
import subprocess as sp
import lts_workflows

FORMAT = '%(levelname)s: %(asctime)-15s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger(__file__)

helpstring = '''
Deploy script for lts_workflows
--------------------------------------

Automate installation of required dependencies to run workflows. You
can request to install dependencies for a single workflow via the
--workflow option. If the conda environment exists, an attempt will be
made to update the environment.

python3 packages will be installed into the current environment
(default) or to environment specified by option --python3. Make sure
to activate this environment before running a workflow. 

python2 packages will be installed into conda environment specified by
the --python2 option ("py2.7" by default).

nextflow packages will be installed into conda environment specified by
the --nextflow option ("nextflow" by default).

Once conda packages have been installed remember to add the bin paths
for python2 and nextflow to your PATH variable:

export PATH="/path/to/nextflow/bin:/path/to/python2/bin:$PATH"


Issues
------

Some conda packages require manual post-installation updates. For
instance, due to licensing issues, the gatk conda package requires you
to run the program 'gatk-register' with a downloaded GATK tarball as
program argument.
'''

WORKFLOWS = ["atacseq", "scrnaseq", "scrnaseq_tx", "variantcalling_gatk"]
ACTIVE_ENV = os.getenv("CONDA_DEFAULT_ENV")
if int(sys.version[0]) != 3:
    logger.error("active environment must have python version 3")
    sys.exit(1)

parser = argparse.ArgumentParser(epilog=helpstring, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-i', '--install', action="store_true", help="actually install packages; by default a dry run is done")
parser.add_argument('-2', '--python2', action="store", help="python2 conda environment name", default="py2.7")
parser.add_argument('-3', '--python3', action="store", help="python3 conda environment name", default=ACTIVE_ENV)
parser.add_argument('-N', '--nextflow', action="store", help="nextflow conda environment name", default="nextflow")
parser.add_argument('-w', '--workflow', action="store",
                    help="install dependencies for given workflow",
                    default="all",
                    choices = ["all"] + WORKFLOWS )
parser.add_argument('-e', '--environment', action="store",
                    help="install dependencies for given environment",
                    default="all")

args = parser.parse_args()


# Find environment files
INSTALLDIR = os.path.dirname(lts_workflows.__file__)

def environment_files(filters=(), workflows=()):
    retval = []
    path = INSTALLDIR
    for path, dirs, files in os.walk(path):
        for f in files:
            if any(f==flt for flt in filters):
                wf = os.path.basename(path)
                if wf in workflows:
                    retval += [os.path.normpath(os.path.join(path, f))]
    return retval

workflows = args.workflow if args.workflow != "all" else WORKFLOWS
if workflows != WORKFLOWS:
    logger.info("restricting installation to workflow {}".format(args.workflow))
    
ENVIRONMENT_FILES = {'python3': environment_files(filters = ("environment.yaml",), workflows=workflows),
                     'python2': environment_files(filters = ("environment-27.yaml", ), workflows=workflows),
                     'nextflow': environment_files(filters = ("environment-nextflow.yaml", ), workflows=workflows)}

output = sp.check_output(['conda', 'env', 'list', '--json'])
# Get name of existing conda envs
condaenvs = [os.path.basename(x) for x in ast.literal_eval(output.decode("utf-8"))['envs']]

# Get names of target environments
targetenvs = [getattr(args, k) for k in sorted(ENVIRONMENT_FILES.keys())]

environments = args.environment if args.environment != "all" else targetenvs
if environments != targetenvs:
    logger.info("restricting installation to environment {}".format(args.environment))

for k, envlist in sorted(ENVIRONMENT_FILES.items()):
    name = getattr(args, k)
    if not name in environments:
        logger.info("Skipping environment {}".format(name))
        continue
    logger.info("Installing dependencies for {} into {} environment".format(k, name))
    env = {'channels':[], 'dependencies':[]}
    for f in envlist:
        with open(f, "r") as fh:
            d = yaml.load(fh)
            env['channels'] = list(set(env['channels'] + d['channels']))
            env['dependencies'] = list(set(env['dependencies'] + d['dependencies']))
    try:
        channels = []
        for c in env['channels']:
            channels.append("-c {}".format(c))
        dependencies = [re.sub("\s+", "", x) for x in env['dependencies']]
        dry_run = "" if args.install else "--dry-run"
        if name not in condaenvs:
            logger.info("creating conda environment {}".format(name))
            proc = sp.Popen("conda create -y {channels} {name} {dryrun} {dependencies}".format(
                channels=" ".join(channels),
                name="-n {}".format(name) if name else "",
                dryrun=dry_run,
                dependencies=" ".join(dependencies)),
                            stdout=None, stderr=None, shell=True)
            out, err = proc.communicate()
        else:
            logger.info("updating conda environment {}".format(name))
            proc = sp.Popen("conda install -y {channels} {name} {dryrun} {dependencies}".format(
                channels=" ".join(channels),
                name="-n {}".format(name) if name else "",
                dryrun=dry_run,
                dependencies=" ".join(dependencies)),
                            stdout=None, stderr=None, shell=True)
            out, err = proc.communicate()

    except:
        raise Exception()
    finally:
        pass
        

if not args.install:
    logger.info("dry run complete; to install packages use the '--install' option")
