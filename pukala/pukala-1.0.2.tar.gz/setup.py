from setuptools import setup, find_packages

setup(
    name = 'pukala',
    version = '1.0.2',
    description = 'dict/list tree generator for cluster deployment',
    long_description = 'check https://gitlab.com/paulsj-80/pukala/blob/master/README.md',

    url = 'https://gitlab.com/paulsj-80/pukala.git', 
    author = 'Pauls Jakovels',
    author_email = 'pauls.jakovels@gmail.com',
    license = 'MIT',
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords = 'yaml tree cluster autodeployment',
    project_urls = {
        'Documentation': 'https://gitlab.com/paulsj-80/pukala/blob/master/README.md',
        'Source': 'https://gitlab.com/paulsj-80/pukala',
    },
    packages = find_packages(exclude=['test', 'samples']),
    install_requires = ['pyyaml', 'simplejson'],
    python_requires = '>2.6, <3',
)
