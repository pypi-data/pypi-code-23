#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
from distutils.core import setup
from distutils.cmd import Command

from distutils.dir_util import remove_tree
from distutils import log
from distutils.command.clean import clean


version_file = os.path.join("sciexp2", "version.py")
with open(version_file) as f:
    code = compile(f.read(), version_file, 'exec')
    exec(code) #, global_vars, local_vars)


# build sphinx docs
sphinx_base = "doc"
sphinx_build = os.path.join(sphinx_base, "_build")
sphinx_ref = os.path.join(sphinx_base, "_reference")

# commands specialized for sphinx
try:
    from sphinx.setup_command import BuildDoc
except:
    BuildDoc = None


class Clean (clean):
    def run(self):
        clean.run(self)
        if self.all:
            for directory in (sphinx_build, sphinx_ref):
                if os.path.exists(directory):
                    print(directory, self.dry_run)
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.debug("'%s' does not exist -- can't clean it",
                              directory)


# run tests
class Test (Command):
    description = "run unit tests"
    user_options = [
        ('test-without-doctest', None, 'test documentation strings'),
        ('test-with-coverage', None, 'provide a coverage report'),
        ('test-with-profile', None, 'profile code run during tests'),
    ]

    def initialize_options(self):
        self.test_without_doctest = False
        self.test_with_coverage = False
        self.test_with_profile = False

    def finalize_options(self):
        pass

    def run(self):
        import sciexp2.tests
        run_ok = sciexp2.tests.run(
            with_doctest=not self.test_without_doctest,
            with_coverage=self.test_with_coverage,
            with_profile=self.test_with_profile,
        )
        if not run_ok:
            sys.exit(1)

opts = dict(name=NAME,
            version=VERSION,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            url=URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            scripts=SCRIPTS,
            requires=REQUIRES,
            install_requires=INSTALL_REQUIRES,
            provides=PROVIDES,
            platforms="any",

            cmdclass={
                'clean': Clean,
                'test': Test,
            },
            command_options={
                'build_sphinx': {
                    'source_dir': ('setup.py', sphinx_base),
                    'build_dir':  ('setup.py', sphinx_build),
                    'all_files':  ('setup.py', True),
                    'version': ('setup.py', VERSION),
                    'release': ('setup.py', VERSION),
                },
            })

if BuildDoc is not None:
    opts["cmdclass"]["build_sphinx"] = BuildDoc

if __name__ == "__main__":
    setup(**opts)
