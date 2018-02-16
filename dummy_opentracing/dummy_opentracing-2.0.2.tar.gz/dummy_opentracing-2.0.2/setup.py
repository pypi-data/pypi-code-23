from setuptools import setup

version = '2.0.2'
setup(
    name='dummy_opentracing',
    version=version,
    url='https://github.com/carlosalberto/opentracing-dummy/',
    download_url='https://github.com/carlosalberto/opentracing-dummy/tarball/'+version,
    license='BSD',
    author='Carlos Alberto Cortez',
    author_email='calberto.cortez@gmail.com',
    description='OpenTracing Dummy package',
    long_description=open('README.rst').read(),
    packages=['dummy_opentracing'],
    platforms='any',
    install_requires=[
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
