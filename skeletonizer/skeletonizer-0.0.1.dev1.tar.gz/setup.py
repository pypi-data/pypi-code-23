"""Hydraulic network skeletonizer

A network skeletonizer aimed at simplifying hydraulic (e.g. water)
distribution networks for water hammer studies.
"""

from setuptools import setup, find_packages
import versioneer
import sys

if sys.version_info < (3, 5):
    sys.exit("Sorry, Python 3.5 or newer is required.")

DOCLINES = __doc__.split("\n")

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Intended Audience :: Information Technology
License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: GIS
Topic :: Scientific/Engineering :: Mathematics
Topic :: Scientific/Engineering :: Physics
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

# Install requirements
with open('requirements.txt', 'r') as req_file:
    install_reqs = req_file.read().split('\n')

setup(
    name='skeletonizer',
    version=versioneer.get_version(),
    maintainer='Tjerk Vreeken',
    author='Tjerk Vreeken',
    description=DOCLINES[0],
    long_description='\n'.join(DOCLINES[2:]),
    url='https://gitlab.com/deltares/skeletonizer/',
    download_url='https://gitlab.com/deltares/skeletonizer/',
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    platforms=['Windows', 'Linux', 'Mac OS-X', 'Unix'],
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=install_reqs,
    tests_require=['nose'],
    test_suite='nose.collector',
    python_requires='>=3.5',
    cmdclass=versioneer.get_cmdclass(),
)
