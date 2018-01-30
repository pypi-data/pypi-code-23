from setuptools import setup

packages = [
    'simplewebdavclient'
]

install_requires = [
    'requests == 2.18.4',
]

tests_require = [
    'pytest',
]

setup(
    name='simplewebdavclient',
    version='1.0.0',
    python_requires='~=3.3',
    description='This is a library used to make WebDav Client Connections simple.',
    keywords='webdav simple',
    url='https://github.com/btr1975/simplewebdavclient',
    author='Benjamin P. Trachtenberg',
    author_email='e_ben_75-python@yahoo.com',
    license='MIT',
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    test_suite='pytest',
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
