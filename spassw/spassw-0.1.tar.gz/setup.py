from setuptools import setup

setup(name='spassw',
    version='0.1',
    description='The simple password generator',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Topic :: System :: Systems Administration',
    ],      
    keywords='Password generation simple secure no+dependency',
    url='http://github.com/iokacha/py-spassw',
    author='OKACHA Ilias',
    author_email='i.okacha@gmail.com',
    license='MIT',
    packages=['spassw'],
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'spassw = spassw.cmdline:spassw_run',
        ]
    },    
    zip_safe=False)