from setuptools import setup, find_packages


setup(
    name='simcli',
    version='0.1.1',
    description='SimpleCli class implementation which can be used to make CLI based utilities',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='cli python',
    url='https://bitbucket.org/deniskhodus/simcli',
    author='Denis Khodus',
    author_email='deniskhodus@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    include_package_data=False,
    zip_safe=False,
)

