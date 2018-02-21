import os
import re

from setuptools import setup


def get_version():
    version_file = os.path.join(
        os.path.dirname(__file__),
        'django_tigger',
        '__init__.py'
    )
    with open(version_file) as f:
        regex = re.compile("^__version__.*?\(([\d]+), *([\d]+), *([\d]+)\).*")
        for line in f:
            m = regex.match(line)
            if m:
                return ".".join(m.groups())


# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

readme = os.path.join(os.path.dirname(__file__), "README.rst")
github = "https://github.com/danielquinn"
with open(readme) as description:
    setup(
        name="django-tigger",
        version=get_version(),
        license="AGPLv3",
        description="Bounce users out of your view by raising an exception",
        long_description=description.read(),
        url="{}/django-tigger".format(github),
        download_url="{}/django-tigger".format(github),
        author="Daniel Quinn",
        author_email="code@danielquinn.org",
        maintainer="Daniel Quinn",
        maintainer_email="code@danielquinn.org",
        packages=["django_tigger"],
        install_requires=["Django>=1.11"],
        classifiers=[
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Topic :: Internet :: WWW/HTTP",
        ],
    )
