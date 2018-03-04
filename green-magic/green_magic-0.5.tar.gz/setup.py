from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='green_magic',
    version='0.5',
    description='The Green Magic library of the Green-Machine',
    long_description=readme(),
    keywords='cannabis strain self-organizing maps visualization',
    classifiers=[
        'Development Status :: 4 - Beta',
        # 'License :: OSI Approved :: GNU General Public License v3.0',
        # 'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)',
        # 'PROGRAMMING LANGUAGE :: PYTHON :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Science/Research',
        ],
    url='https://github.com/boromir674/green_machine/tree/dev/gmagic',
    author='Konstantinos',
    author_email='k.lampridis@hotmail.com',
    license='GNU GPLv3',
    packages=['green_magic', 'green_magic.clustering'],
    install_requires=['nltk', 'gensim', 'sklearn', 'matplotlib', 'numpy', 'somoclu'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    zip_safe=False
)


