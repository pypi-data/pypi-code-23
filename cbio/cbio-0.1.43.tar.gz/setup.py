from setuptools import setup, find_packages
import re
import ast

__author__ = "Cristian Perez"
__copyright__ = "Copyright 2017, Cristian Perz"
__email__ = "Vilero89@gmail.com"
__license__ = "MIT"

try:
    from setuptools import setup
except ImportError:
    print("Please install setuptools before installing snakemake.",
          file=sys.stderr)
    exit(1)

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('cbio/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='cbio',
    version=version,
    description='Package with bioinformatical utilities',
    url='https://github.com/Cristian-pg/cbio',
    author='Cristian Perez',
    author_email='Vilero89@gmail.com',
    license='GNU General Public License v3.0',
    packages=find_packages(),
    zip_safe=False,
    python_requires='>=3',
    package_data={'': ['*.css', '*.sh', '*.html']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        "console_scripts":
            [
                "cbio=cbio:main",
            ]
    },
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
        'tailer',
        'biomart',
        'coloredlogs'
    ],
)
