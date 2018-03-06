from setuptools import setup, find_packages
from collections import defaultdict
from pathlib import Path
import os

setup_args = dict(
    version='2.0.0',
    name='orcae',
    description='Online Resource for Community Annotation of Eukaryotes',
    long_description='Online Resource for Community Annotation of Eukaryotes, see http://bioinformatics.psb.ugent.be/orcae/. This is a placeholder to reserve the Python root package name "orcae".',
    url='https://gitlab.psb.ugent.be/beg-orcae/orcae',
    author='BEG/VIB/UGent',
    author_email='beg-orcae@psb.ugent.be',
    license='AGPL3',
    keywords='bioinformatics',
    packages=[],
    install_requires=[
    ],
    extras_require={
    },
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Natural Language :: English',
    ],
)

# Generate extras_require['all'], union of all extras
all_extra_dependencies = []
for dependencies in setup_args['extras_require'].values():
    all_extra_dependencies.extend(dependencies)
all_extra_dependencies = list(set(all_extra_dependencies))
setup_args['extras_require']['all'] = all_extra_dependencies

# Generate package data
#
# Anything placed underneath a directory named 'data' in a package, is added to
# the package_data of that package; i.e. included in the sdist/bdist and
# accessible via pkg_resources.resource_*
project_root = Path(__file__).parent
package_data = defaultdict(list)
for package in setup_args['packages']:
    package_dir = project_root / package.replace('.', '/')
    data_dir = package_dir / 'data'
    if data_dir.exists() and not (data_dir / '__init__.py').exists():
        # Found a data dir
        for parent, _, files in os.walk(str(data_dir)):
            package_data[package].extend(str((data_dir / parent / file).relative_to(package_dir)) for file in files)
setup_args['package_data'] = {k: sorted(v) for k,v in package_data.items()}  # sort to avoid unnecessary git diffs

# setup
setup(**setup_args)
