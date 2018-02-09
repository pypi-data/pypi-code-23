# Copyright 2017 The NPU Compiler Authors. All Rights Reserved.
#
# Licensed under the Proprietary License;
# you may not use this file except in compliance with the License.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from setuptools import find_packages, setup
from codecs import open
from os import path

from npu_compiler.config import Config

REQUIRED_PACKAGES = [
    'numpy',
    'pyyaml',
    'wheel',
    'six',
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='npu_compiler',
    version=Config.VERSION,
    description='produce NPU instructions',
    long_description=long_description,
    url='http://www.gxdnn.org/',
    author='Hangzhou Nationalchip Inc.',
    author_email='zhengdi@nationalchip.com',
    license='MIT Licence',

    # PyPI package information.
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        ],

    keywords='npu gxdnn nationalchip',

    # Contained modules and scripts.
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,

    package_data={
        'npu_compiler': ['*.so','*.py', 'gen_cmd/output/libnpu_compiler_mpw.so',\
            'gen_cmd/output/libnpu_compiler_nre.so', 'tensorflow_freeze/*.py', 'tensorflow_freeze/*.so',\
            'rebuild_ckpt/*.py', 'rebuild_ckpt/*.so', 'rebuild_ckpt/c_support/libop_compress.so',\
            'rebuild_ckpt/config.yaml', 'gen_cmd/fw/*.bin']
    },
    scripts=['gxnpuc', 'gxnpudebug', 'gxnpu_rebuild_ckpt'],
    entry_points={
    },
    )
