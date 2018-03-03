"""urlsupport"""

# pylint: disable=C0103
#                          Invalid name for type variable

import re
import shutil
import urllib
import sumolib.system

__version__="3.3" #VERSION#

assert __version__==sumolib.system.__version__

rx_url= re.compile(r'([A-Za-z][A-Za-z0-9\.+-]*):')

urllib_schemes= set(("http","ftp","file"))

def assert_scp():
    """test if scp exists."""
    try:
        sumolib.system.test_program("scp")
    except IOError, e:
        if "usage" in str(e):
            # scp was found, but it returned an error
            sumolib.system.program_tests.add("scp")
            return

def get(url, dest, verbose, dry_run):
    """Get by url."""
    m= rx_url.match(url)
    if m is None:
        # try to copy:
        if verbose:
            print "shutil.copyfile(%s, %s)\n" % (repr(url), repr(dest))
        shutil.copyfile(url, dest)
        return
    scheme_name= m.group(1)
    if scheme_name=="ssh":
        if not url.startswith("ssh://"):
            raise ValueError("error, ssh url '%s' not supported" % url)
        st= url.replace("ssh://","",1)
        assert_scp()
        cmd= "scp \"%s\" \"%s\"" % (st, dest)
        sumolib.system.system(cmd, False, False, verbose, dry_run)
        return
    if scheme_name in urllib_schemes:
        if verbose:
            print "urllib.urlretrieve(%s, %s)\n" % (repr(url), repr(dest))
        urllib.urlretrieve(url, dest)
        return
    raise ValueError("error, url '%s' not supported" % url)

