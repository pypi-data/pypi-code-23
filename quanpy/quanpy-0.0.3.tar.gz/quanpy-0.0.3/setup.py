from setuptools import setup, find_packages

__version__ = '0.0.3'
requires = []

setup(
    name='quanpy',
    version=__version__,
    description='Quantum Annealing Algorithm Library',
    long_description='',
    url='https://github.com/ymurata/quanpy',
    author='ymurata',
    author_email='m.yuma0531@gmail.com',
    license='Apach 2.0',
    keywords='quantum annealing',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=requires,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
    ],
)
