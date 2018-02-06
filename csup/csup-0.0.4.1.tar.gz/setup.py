from setuptools import setup

setup(
    name='csup',
    version='0.0.4.1',
    description='Container Security UPloading and reporting tool (CSUP)',
    long_description='Commandline tool to upload, check the status, and report on docker images in Tenable\'s Container Security product',
    author='Steven McGrath <smcgrath@tenable.com>',
    author_email='smcgrath@tenable.com',
    url='',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='development docker security',
    packages=['csup'],
    install_requires=[
        'python-dateutil>=2.6',
        'requests>=2.18',
        'docker>=2.6',
        'colorama>=0.3',
    ],
    entry_points={
        'console_scripts': [
            'csup=csup:main'
        ],
    },
)