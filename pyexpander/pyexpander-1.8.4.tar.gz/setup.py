#!/usr/bin/env python
"""
setup.py file for pyexpander.

See http://docs.python.org/install
on how to use setup.py
"""

# see : http://stackoverflow.com/questions/25337706/setuptools-vs-distutils-why-is-distutils-still-a-thing
# maybe use this in the future:
#
# if len(sys.argv) >= 2 and ('--help' in sys.argv[1:] or
#         sys.argv[1] in ('--help-commands', 'egg_info', '--version',
#                         'clean')):
#     # Use setuptools for these commands (they don't work well or at all
#     # with distutils).  For normal builds use distutils.
#     try:
#         from setuptools import setup
#     except ImportError:
#         from distutils.core import setup

from distutils.core import setup
import os.path
import sys
import subprocess

# pylint: disable=invalid-name

pjoin= os.path.join

if sys.version_info[0] == 2:
    base_name= 'python'
    base_dir = 'python2'
    pchar=""
elif sys.version_info[0] == 3:
    base_name= 'python3'
    base_dir = 'python3'
    pchar="3"

# note: the following version number should be equal with the one
# shown by expander.py:
__version__= "1.8.4" #VERSION#

# utilities -------------------------

def find_files(path):
    """find files and directories below a given path.

    here is an example of the returned data structure:
    {'doc/_build/html': ['objects.inv', 'searchindex.js', 'index.html'],
     'doc/_build': [],
     'doc/_build/html/_sources': ['license.txt', 'index.txt']
     'doc/_build/doctrees': ['SDshell.doctree', 'license.doctree']
    }
    """
    paths= {}
    for dirpath, _, filenames in os.walk(path):
        paths[dirpath]= filenames
    return paths

def pathsplit(path):
    """splits a path into pieces.

    Here are some examples:
    >>> pathsplit("A")
    ['A']
    >>> pathsplit("A/B")
    ['A', 'B']
    >>> pathsplit("A/B/C")
    ['A', 'B', 'C']
    >>> pathsplit("A/B.x/C.y")
    ['A', 'B.x', 'C.y']
    """
    l= []
    while True:
        (head,tail)=os.path.split(path)
        l.append(tail)
        if not head:
            break
        path= head
    l.reverse()
    return l

def path_rebase(path, base):
    """rebases a path.

    Here are some examples:
    >>> path_rebase("doc/_build/html/_sources","doc/_build")
    'html/_sources'
    >>> path_rebase("doc/_build/html/_sources","doc/_build/html")
    '_sources'
    >>> path_rebase("doc/_build/html/_sources","doc")
    '_build/html/_sources'
    >>> path_rebase("doc/_build/html/_sources","doc/_bduild")
    'doc/_build/html/_sources'
    """
    path_l= pathsplit(path)
    base_l= pathsplit(base)
    if len(path_l)<len(base_l):
        return path
    for (i, base_elm) in enumerate(base_l):
        if base_elm!=path_l[i]:
            return path
    if len(path_l)==len(base_l):
        return ""
    return os.path.join(*path_l[len(base_l):])

def data_statements(install_path, source_path):
    """create data statements for arbitrary files."""
    filedict= find_files(source_path)
    data_dict= {}
    for (path,files) in filedict.items():
        subdir= path_rebase(path, source_path)
        if subdir != "":
            destpath= os.path.join(install_path, subdir)
        else:
            destpath= install_path
        for f in files:
            l= data_dict.get(destpath)
            if l is None:
                l= []
                data_dict[destpath]= l
            l.append(os.path.join(path, f))
    return list(data_dict.items())

# main      -------------------------

doc_install_dir= os.path.join("share", "doc",
                              "pyexpander%s-%s" % (pchar, __version__))
html_install_dir= os.path.join(doc_install_dir, "html")

html_build_dir= os.path.join("doc","_build","html")

## create HTML documentation if it doesn't already exist:
if not os.path.exists(html_build_dir):
    # "make -C doc html":
    subprocess.check_call([os.path.join("administration_tools","doc-rebuild.sh")])

data_files_list= [(doc_install_dir, ["README", "LICENSE"])]

# add all generated html documentation to data_files_list:
data_files_list.extend(data_statements(html_install_dir, html_build_dir))

name= 'pyexpander'
if "bdist_rpm" in sys.argv:
    name= base_name+"-"+name

setup(name=name,
      version= __version__,
      description='a powerful macro processing language',
      author='Goetz Pfeiffer',
      author_email='Goetz.Pfeiffer@helmholtz-berlin.de',
      url='https://goetzpf.bitbucket.io/pyexpander/index.html',
      download_url='https://bitbucket.org/goetzpf/pyexpander/downloads',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development',
          'Topic :: Software Development :: Pre-processors',
          'Topic :: Text Processing',
          'Topic :: Utilities',
          ],
      packages=['pyexpander'],
      package_dir= {'pyexpander': pjoin(base_dir, 'pyexpander')},
      # the data_files parameter is especially needed for the
      # rpm file generation:
      data_files= data_files_list,
      license= "GPLv3",
      scripts=[pjoin(base_dir, "bin", p) \
               for p in ['expander%s.py' % pchar,
                         'msi2pyexpander%s.py' % pchar]
              ],
     )
