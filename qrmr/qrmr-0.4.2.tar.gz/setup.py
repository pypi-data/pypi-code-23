#   ____  _____  __  __ _____
#  / __ \|  __ \|  \/  |  __ \
# | |  | | |__) | \  / | |__) |
# | |  | |  _  /| |\/| |  _  /
# | |__| | | \ \| |  | | | \ \
#  \___\_\_|  \_\_|  |_|_|  \_\
#
# Highly opinionated Amazon Web Services (AWS) terminal login toolkit, focused on
# enforcing AWS Multi-Factor Authentication (MFA).
#
# Find us on: https://qrmr.io
#
# (c)Copyright 2017 - 2018, all rights reserved by QRMR / ALDG / Alexander L. de Goeij.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from setuptools import setup, find_packages
from qrmr import __version__


setup(
    name="qrmr",
    version=__version__,
    author="Alexander L. de Goeij",
    author_email="mail@aldg.nl",
    description=("Terminal login toolkit for Amazon Web Services (AWS) enforcing "
                 "and simplifying use of Multi-Factor Authentication (MFA)."),
    license="NO_LICENSE_YET",
    keywords="cloud aws cli login mfa otp session token",
    url="https://gitlab.com/qrmr/qrmr",
    packages=find_packages(),
    install_requires=['future', 'colorlog',
                      'boto3', 'configparser', 'requests'],
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            "qrmr=qrmr.qrmr:main",
        ]
    },
)
