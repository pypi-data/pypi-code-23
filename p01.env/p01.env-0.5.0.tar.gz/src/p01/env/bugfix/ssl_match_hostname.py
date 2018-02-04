###############################################################################
#
# Copyright (c) 2018 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""backport.ssl_match_hostname bugfix

The python ssl.py match_hostname is broken. The hostname doesn't get validated
based on IP Address defined in certificates (oid:1.2.3.4.5.5 IP:10.8.0.211)
The error raised says that the hostname doesn't match the given IP which is
wrong. This is because the IP Address is just ignored and not validated:

This method will apply the patch for gevent.
gevent-1.2.2\gevent-1.2.2\_ssl3.py
gevent-1.2.2\gevent-1.2.2\_sslgte279.py


The urllib3 is using the backport.ssl_match_hostname package and imports the
patch if the package is installed. The gevent package is just importing the
default python ssl.py and not the backport fix.
"""
__docformat__ = "reStructuredText"

import sys

try:
    import ssl
except ImportError:
    raise ValueError("Can't apply ssl_match_hostname if ssl is not installed")

try:
    from backports.ssl_match_hostname import match_hostname
except ImportError:
    raise ValueError(
        "Can't apply ssl_match_hostname if backports.ssl_match_hostname is not "
        "installed. Add backports.ssl_match_hostname to your dependencies or "
        "Use eggs = p01.env [ssl] in your buildout parts")

PY2 = sys.version_info[0] == 2


###############################################################################
#
# python 2.7 ssl.match_hostname patch

def setUpPythonSSLMatchHostnameBugfix(quiet=False):
    """Patch python ssl match_hostname method"""
    ssl.match_hostname = match_hostname
    if not quiet:
        sys.stderr.write(
            "PATCH: xcore.bugfix.ssl:setUpPythonSSLMatchHostnameBugfix")


###############################################################################
#
# gevent ssl.match_hostname patch

def setUpGeventSSLMatchHostnameBugfix(quiet=False):
    """Patch gevent match_hostname method"""
    try:
        import gevent
    except ImportError:
        raise ValueError(
            "Can't apply ssl_match_hostname for gevent if gevent is not "
            "installed. Add gevent to your dependencies or Use eggs = gevent "
            "in your buildout parts")

    if PY2:
        # patch gevent._sslgte279
        try:
            import gevent._sslgte279
            gevent._sslgte279.match_hostname = match_hostname
        except ImportError:
            raise ValueError(
                "This patch is not compatible with your gevent version. Make "
                "sure your gevent version provides the gevent._sslgte279 "
                "module.")

    else:
        # patch gevent._sslgte279
        try:
            import gevent._ssl3
            gevent._ssl3.match_hostname = match_hostname
        except ImportError:
            raise ValueError(
                "This patch is not compatible with your gevent version. Make "
                "sure your gevent version provides the gevent._ssl3 module.")
    try:
        # patch gevent.ssl
        import gevent.ssl
        gevent.ssl.match_hostname = match_hostname
    except ImportError:
        raise ValueError(
            "This patch is not compatible with your gevent version. Make "
            "sure your gevent version provides the gevent.ssl module.")
    if not quiet:
        sys.stderr.write(
            "PATCH: p01.env.bugfix.ssl:setUpGeventSSLMatchHostnameBugfix")
