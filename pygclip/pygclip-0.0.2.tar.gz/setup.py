import io
import re
import sys
from setuptools import setup

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported.')

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('pygclip/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='pygclip',
    version=version,
    license='MIT',
    author='Bryan Lee McKelvey',
    author_email='bryan.mckelvey@gmail.com',
    description='Pygmentize to clipboard for macOS.',
    long_description=readme,
    packages=['pygclip'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pygments',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    extras_require={
        'dev': [
            'coverage',
            'pytest>=3',
            'sphinx',
            'tox',
        ],
    },
    entry_points={
        'console_scripts': [
            'pygclip = pygclip.cli:main',
        ],
    },
)
