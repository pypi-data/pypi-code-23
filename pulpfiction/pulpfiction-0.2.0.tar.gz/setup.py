import io
import re
from setuptools import setup


with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('pulpfiction/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='pulpfiction',
    version=version,
    url='https://github.com/kelvintaywl/pulpfiction',
    author='Kelvin Tay',
    author_email='kelvintaywl@gmail.com',
    maintainer='Kelvin Tay',
    maintainer_email='kelvintaywl@gmail.com',
    description='A simple utility tool to detect non-English comments in code',
    long_description=readme,
    packages=['pulpfiction'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pygments>=2.2.0',
        'langdetect>=1.0.7',
        'click>=6.7',
    ],
    extras_require={
        'dev': [
            'flake8>=3.5.0'
        ]
    },
    python_requires='>=3',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'jules = pulpfiction.cli:main',
        ],
    },
)
