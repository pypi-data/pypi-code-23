from setuptools import setup, find_packages


setup(
    name='dynamic_pytables_where_condition',
    version='1.1.0',
    url='https://bitbucket.org/petar/dynamic_pytables_where_condition',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Python library that dynamically constructs a PyTables where '\
                'condition from the supplied keyword arguments.',
    long_description=open('README').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    platforms='any',
    py_modules=['dynamic_pytables_where_condition'],
)
