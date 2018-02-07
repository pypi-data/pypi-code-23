from setuptools import setup, find_packages
from pathlib import Path
from typing import List

SHORT_DESCRIPTION = 'Create Foliant projects from templates.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION

def get_templates(path: Path) -> List[str]:
    '''List all files in ``templates`` directory, including all subdirectories.

    The resulting list contains UNIX-like relative paths starting with ``templates``.
    '''

    result = []

    for item in path.glob('**/*'):
        if item.is_file() and not item.name.startswith('_'):
            result.append(item.relative_to(path.parent).as_posix())

    return result

setup(
    name='foliantcontrib.init',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    version='1.0.3',
    author='Konstantin Molchanov',
    author_email='moigagoo@live.com',
    url='https://github.com/foliant-docs/foliantcontrib.init',
    packages=['foliant.cli.init'],
    package_data={'foliant.cli.init': get_templates(Path('foliant/cli/init/templates'))},
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.0',
        'python-slugify'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ]
)
