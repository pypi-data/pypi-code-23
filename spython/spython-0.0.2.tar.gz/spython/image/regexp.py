#  Docker URIs

import re

#- registry must include a url extension (e.g., docker.io)
#- name space is optional'
#- these rules are from Singularity shell.py (libexec/python/shell.py)
#- https://github.com/singularityware/singularity

_docker = re.compile(
    # A registry (not required) will have a '.' or ':', cannot have '/' or '@',
    # and terminal=ted by '/'. It also includes the port
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    # A namespace (not required), cannot have ':' or '/', also ends with '/'. 
    "(?P<namespace>(?:[^:@/]+/)+)?"
    # REQUIRED: Match a repository name, with any character but ':' or '/'
    "(?P<repo>[^:@/]+)"
    # Match :tag (not required)
    "(?::(?P<tag>[^:@]+))?"
    # Match @digest (optional) A digest is a shasum typically
    "(?:@(?P<version>.+))?"
    # there cannot be trailing characters on the string
    "$")

# Docker images can have a reduced format (e.g., registry:port/repo)
# or ( registry.com/repo ). The registry must have a '.' or ':' (for port)
# The user can also just provide a repository (e.g., ubuntu)

_docker_simple = re.compile(
    # match a registry, optional, may include a : or ., but not a @
    "(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
    # REQUIRED Match a repo name, Any character but ':' or '/'
    "(?P<repo>[^:@/]+)"
    # Match :tag (optional)
    "(?::(?P<tag>[^:@]+))?"
    # Match @digest (optional)
    "(?:@(?P<version>.+))?"
    # No left over string
    "$"
    # dummy group that will never match, but will add a 'namespace' entry
    "(?P<namespace>.)?")


# Singularity Hub (or Registry) with uri shub://
# registry[:port]/namespace[/more/namespaces]/repo
# or namespace/repo, at least one namespace is required

_shub = re.compile(
    # Match registry, if specified (defaults to Singularity Hub)
    "(?:(?P<registry>[^/@]+)/)?"
    # Match a namespace, matched as any characters but
    # ':' or '@', ended by a '/'. Match ends with '/'
    "(?P<namespace>(?:[^:@/]+/)+)"
    # REQUIRED Match a repository name, not including ':' or '/'
    "(?P<repo>[^:@/]+)"
    # Match :tag (optional)
    "(?::(?P<tag>[^:@]+))?"
    # Match @digest (optional)
    "(?:@(?P<version>.+))?"
    # we need to match the whole string (again)
    "$")
