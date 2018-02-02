"""P4Python - Python interface to Perforce API

Perforce is the fast SCM system at www.perforce.com.
This package provides a simple interface from Python wrapping the
Perforce C++ API to gain performance and ease of coding.
Similar to interfaces available for Ruby and Perl.

"""
from __future__ import print_function

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: Freely Distributable
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Version Control
Topic :: Software Development
Topic :: Utilities
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: MacOS :: MacOS X
"""

# Customisations needed to use to build:
# 1. Set directory for p4api in setup.cfg

# See notes in P4API documentation for building with API on different
# platforms:
#   http://www.perforce.com/perforce/doc.current/manuals/p4api/02_clientprog.html

MIN_SSL_VERSION=100
# MIN_SSL_RELEASE='e' # currently not restricting builds for any OpenSSL > 1.0.0

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import os, os.path, sys, re, shutil, stat
import subprocess
from tools.P4APIFtp import P4APIFtp
from tools.PlatformInfo import PlatformInfo
from tools.VersionInfo import VersionInfo


if sys.version_info < (3,0):
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser


global_dist_directory = "p4python-"

doclines = __doc__.split("\n")

NAME = "p4python"
VERSION = "2017.1"
PY_MODULES = ["P4"]
P4_API_DIR = "p4api"
DESCRIPTION=doclines[0]
AUTHOR="Perforce Software Inc"
MAINTAINER="Perforce Software Inc"
AUTHOR_EMAIL="sknop@perforce.com"
MAINTAINER_EMAIL="support@perforce.com"
LICENSE="LICENSE.txt"
URL="http://www.perforce.com"
KEYWORDS="Perforce perforce P4Python"

P4_CONFIG_FILE="setup.cfg"
P4_CONFIG_SECTION="p4python_config"
P4_CONFIG_P4APIDIR="p4_api"
P4_CONFIG_SSLDIR="p4_ssl"

P4_DOC_RELNOTES="../p4-doc/user/p4pythonnotes.txt"
P4_RELNOTES="RELNOTES.txt"


def copyReleaseNotes():
    """Copies the relnotes from the doc directory to the local directory if they exist
    Returns True if the release notes were copied, otherwise False
    """
    if os.path.exists(P4_DOC_RELNOTES):
      try:
        shutil.copy(P4_DOC_RELNOTES, P4_RELNOTES)
        return True
      except Exception as e:
        print (e)
        return False
    else:
        return False


def deleteReleaseNotes():
    """Removes RELNOTES.txt from the current directory again"""
    os.chmod(P4_RELNOTES, stat.S_IWRITE)
    os.remove(P4_RELNOTES)


def do_setup(p4_api_dir, ssl):
    global global_dist_directory

    try:
      apiVersion = VersionInfo(p4_api_dir)
      releaseVersion = VersionInfo(".")
    except IOError:
      print ("Cannot find Version file in API dir or distribution dir.")
      print ("API path = ", p4_api_dir)
      exit(1)

    ryear = int(apiVersion.release_year)
    rversion = int(apiVersion.release_version)
    global_dist_directory += releaseVersion.getDistVersion()

    if (ryear < 2012) or (ryear == 2012 and rversion < 2):
      print ("API Release %s.%s not supported. Minimum requirement is 2012.2." % (ryear, rversion))
      print ("Please download a more recent API release from the Perforce ftp site.")
      exit(1)
    else:
      print ("API Release %s.%s" % (ryear, rversion))

    inc_path = [p4_api_dir, os.path.join(p4_api_dir, "include", "p4")]
    lib_path = [p4_api_dir, os.path.join(p4_api_dir, "lib")]
    if ssl:
        lib_path.append( ssl )

    info = PlatformInfo(apiVersion, releaseVersion, ssl)

    setup(name=NAME,
          version=releaseVersion.getDistVersion(),
          description=DESCRIPTION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          license=LICENSE,
          url=URL,
          keywords=KEYWORDS,
          classifiers = [ x for x in classifiers.split("\n") if x ],
          long_description = "\n".join(doclines[2:]),
          py_modules=PY_MODULES,
          ext_modules=[Extension("P4API", ["P4API.cpp", "PythonClientAPI.cpp",
                                            "PythonClientUser.cpp", "SpecMgr.cpp",
                                            "P4Result.cpp",
                                            "PythonMergeData.cpp", "P4MapMaker.cpp",
                                            "PythonSpecData.cpp", "PythonMessage.cpp",
                                            "PythonActionMergeData.cpp", "PythonClientProgress.cpp",
                                            "P4PythonDebug.cpp"],
                         include_dirs = inc_path,
                         library_dirs = lib_path,
                         libraries = info.libraries,
                         extra_compile_args = info.extra_compile_args,
                         define_macros = info.define_macros,
                         extra_link_args = info.extra_link_args
                        )])


def get_api_dir(version):
    loaded_from_ftp = False
    
    if '--apidir' in sys.argv:
        index = sys.argv.index("--apidir")
        if index < len(sys.argv) - 1:
            p4_api_dir = sys.argv[index + 1]
            del sys.argv[index:index+2]
        else:
            print ("Error: --apidir needs API dir as an argument")
            sys.exit(99)
    else:
        config = ConfigParser()
        config.read(P4_CONFIG_FILE)
        p4_api_dir = None
        if config.has_section(P4_CONFIG_SECTION):
            if config.has_option(P4_CONFIG_SECTION, P4_CONFIG_P4APIDIR):
                p4_api_dir = config.get(P4_CONFIG_SECTION, P4_CONFIG_P4APIDIR)
        if not p4_api_dir:
            # try to download the API from the ftp site
            print( "Attempting to load API from ftp.perforce.com" )
            p4ftp = P4APIFtp()
            p4_api_dir = p4ftp.loadAPI(version)
            print( "Loaded API into {0}".format(p4_api_dir) )
            loaded_from_ftp = True

    return ( p4_api_dir, loaded_from_ftp )


def force_remove_file(function, path, excinfo):
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )


def rreplace(s, old, new, occurrence=1):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def check_ssl():
    try:
        (version_string,err) = subprocess.Popen(["openssl","version"], stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    except IOError:
        print("****************************************************",file=sys.stderr)
        print("No openssl in path and no ssl library path specified", file=sys.stderr)
        print("****************************************************",file=sys.stderr)
        return None
    
    if err:
        print("****************************************************",file=sys.stderr)
        print("Cannot determine the version of openssl", file=sys.stderr)
        print("****************************************************",file=sys.stderr)
        return None

    if type(version_string) == bytes:
        version_string = version_string.decode('utf8')
    
    pattern = re.compile("OpenSSL (\d)\.(\d)\.(\d)(\S+)\s+\d+ \S+ \d+")
    match = pattern.match(version_string)
    if match:
        version = int(match.group(1)) * 100 + int(match.group(2)) * 10 + int(match.group(3)) * 1
        if version >= MIN_SSL_VERSION:
            release = match.group(4)
            for p in os.environ["PATH"].split(os.pathsep):
                pathToFile = os.path.join(p, "openssl")
                if os.path.exists(pathToFile) and os.access(pathToFile, os.X_OK):
                    libpath = rreplace(p,"bin","lib")
                    if os.path.exists(libpath) and os.path.isdir(libpath):
                        return libpath
                    else:
                        print("****************************************************",file=sys.stderr)
                        print("Calculated path {} for SSL does not exist".format(libpath), file=sys.stderr)
                        print("****************************************************",file=sys.stderr)
                        return None
        else:
            print("***************************************",file=sys.stderr)
            print("Minimum SSL release required is 1.0.0",file=sys.stderr)
            print("***************************************",file=sys.stderr)
    else:
        print("****************************************************",file=sys.stderr)
        print("Cannot match OpenSSL Version string '{0}'".format(version_string),file=sys.stderr)
        print("****************************************************",file=sys.stderr)
    
    return None

def remove_ssl(argv):
    index = argv.index("--ssl")
    if index < len(argv) - 1:
        ssl = argv[index + 1]
        del argv[index:index+2]
    else:
        ssl = ""
        del argv[index:index+1]
    return ssl

def cleanup_api(p4_api_dir):
    base = os.path.dirname(p4_api_dir)
    #===========================================================================
    # Delete p4api.tgz and p4_api_dir
    #===========================================================================
    
    print("Deleting temporary files from '{}'".format(base))
    
    tarfile = os.path.join(base, "p4api.tgz")
    os.unlink(tarfile)
    shutil.rmtree(p4_api_dir)
    
if __name__ == "__main__":

    version = VersionInfo(".")

    (p4_api_dir, loaded_from_ftp) = get_api_dir(version.getVersion())
    ssl = None
    
    if 'sdist' in sys.argv:
        # Don't use hard links when building source distribution.
        # It's great, apart from under VirtualBox where it falls
        # apart due to a bug
        try:
            del os.link
        except:
            pass

        if os.path.exists(P4_RELNOTES):
            deleteReleaseNotes()
        copyReleaseNotes()

        distdir = global_dist_directory + version.getDistVersion()
        if os.path.exists(distdir):
            shutil.rmtree(distdir, False, force_remove_file)

        # option not needed for source builds, but --ssl in the options confuses setuptools

        if '--ssl' in sys.argv:
            remove_ssl(sys.argv)

    else:
        if '--ssl' in sys.argv:
            ssl = remove_ssl(sys.argv)
        else:
            config = ConfigParser()
            config.read(P4_CONFIG_FILE)

            if config.has_section(P4_CONFIG_SECTION):
                if config.has_option(P4_CONFIG_SECTION, P4_CONFIG_SSLDIR):
                    ssl = config.get(P4_CONFIG_SECTION, P4_CONFIG_SSLDIR)

        if ssl == "":
            # check version of SSL via 'openssl version'
            ssl = check_ssl() # return None if illegal or too old
    
        if ssl == None:
            print("***********************************************", file=sys.stderr)
            print("** Cannot build P4Python without SSL support **", file=sys.stderr)
            print("***********************************************", file=sys.stderr)
            sys.exit(1)

    do_setup(p4_api_dir, ssl)
    
    if loaded_from_ftp:
        cleanup_api(p4_api_dir)
