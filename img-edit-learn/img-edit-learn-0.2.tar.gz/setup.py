# from glob import glob
from pkg_resources import parse_version
from setuptools import setup, find_packages

# Read requirements
with open('requirements.txt', 'r') as fh:
    reqs = [str(x).strip() for x in fh.readlines()]

data_files = ['README.md']  # + glob('conf/*')

# Read from and write to the version file
with open('ielearn/_version.py', 'r+') as fh:
    version_found = False
    while not version_found:
        vpos = fh.tell()
        line = fh.readline()
        if line == '':
            # reached the end of the file without finding the version tag
            raise ValueError("__version__ not found in _version.py.")
        elif line.startswith('__version__'):
            exec line
            version_found = True

setup(
    name="img-edit-learn",
    version=__version__,
    description="Machine learning for Personalized Image Editing",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering"
    ],
    url="https://github.com/aagnone3/img-edit-learn",
    packages=find_packages(exclude=['*.test', 'test']),
    author="Anthony Agnone",
    author_email="anthonyagnone@gmail.com",
    license="MIT",
    zip_safe=False,
    install_requires=reqs,
    data_files=[('share/aagnone/img-edit-learn', data_files)],
    include_package_data=True
)
