# Copyright 2017 Xaptum, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License

from setuptools import setup
import os
import distutils.cmd


class CTypesGenException(Exception):
    pass


class AddLibraryPathCommand(distutils.cmd.Command):
    description = 'add path to xaptum-tpm library search path'
    user_options = [('xtpm-lib=', None, 'library search path for Xaptum-TPM library'),]

    def initialize_options(self):
        self.xtpm_lib = None

    def finalize_options(self):
        self.xtpm_lib = os.path.abspath(self.xtpm_lib)

    def run(self):
        if self.xtpm_lib:
            with open('xaptum/tpm/_extra_search_dir.py', 'w') as out_file:
                out_file.write('_other_dirs = [\'' + self.xtpm_lib + '\']')


setup(
        name = 'xaptum-tpm-python',
        version = '0.4.0',
        description = 'Python wrapper for Xaptum TPM',
        author = 'Xaptum, Inc.',
        author_email = 'sales@xaptum.com',
        license = 'Apache 2.0',
        url = 'https://github.com/xaptum/xaptum-tpm-python',
        packages = ['xaptum', 'xaptum.tpm'],
        test_suite = 'nose.collector',
        cmdclass={
            'addlibpath': AddLibraryPathCommand,
        },
        )
