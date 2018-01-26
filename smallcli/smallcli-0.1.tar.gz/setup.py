from setuptools import setup
from setuptools import find_packages

install_requires = [
    'pygments==2.2.0',
    'prompt_toolkit==1.0.15',
    'gevent==1.2.2',
    'importlib==1.0.4',
    'termcolor==1.1.0'
]
test_requires = []

setup(
    name='smallcli',
    version='0.1',
    description="CLI framework for automation scripts",
    author="S.Suresh Kumar",
    author_email="sureshkumarr.s@gmail.com",
    url="https://github.com/knetsolutions/smallcli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    keywords='cli',
    scripts=[],
    license="Apache",
    entry_points={
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ]
)
