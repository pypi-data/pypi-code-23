import os
from setuptools import setup
import json

exec(open("./rxw/_version.py").read())


def requirements_from_pipfile(pipfile=None):
    if pipfile is None:
        pipfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'Pipfile.lock')
    lock_data = json.load(open(pipfile))
    return [package_name for package_name in
            lock_data.get('default', {}).keys()]


install_requires = requirements_from_pipfile()


setup(
    name="rx-weather",
    version=__version__,
    packages=[
        'rxw',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            'rx-weather=rxw.app:main'
    },

    # metadata for upload to PyPI
    author="Norm Barnard",
    author_email="norm@normbarnard.com",
    description="demo app to fetch weather using requests and rxpy",
    license="MIT",
    keywords="rx, python, weather, demo",
    url="https://github.com/barnardn/rx_weather",
    python_requires='~=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
)
