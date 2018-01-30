from setuptools import setup, find_packages


setup(
    name='pc23',
    version='1.0.1',
    description='PC23 Python 2.x - 3.x compatibility library',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='pc23 compatibility',
    url='https://bitbucket.org/deniskhodus/pc23',
    author='Denis Khodus',
    author_email='deniskhodus@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    include_package_data=False,
    zip_safe=False
)

