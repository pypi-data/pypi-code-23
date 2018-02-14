from setuptools import setup, find_packages
from logorama import __version__, __package__

setup(
    name=__package__,
    version=__version__,
    description='Light weight colorful python logger',
    author='Kapil Sharma',
    author_email='sharmakapil8@gmail.com',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'pytz'
    ],
    entry_points={
    },
    include_package_data=True,
    zip_safe=False
)