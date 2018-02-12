from setuptools import setup, find_packages, Command
import shutil
import os


class CleanUpCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sourceToDelete = ["bymtesting.egg-info"]
        for f in sourceToDelete:
            if os.path.exists(os.path.join(os.getcwd(), f)):
                shutil.rmtree(f)
                print("removed {}".format(f))


currentVersion = "1.0.3"

setup(
    name="bymtesting",
    version=currentVersion,
    description="A python framework for integrtion testing av asp.net core web apies.",
    author="Oslo Kommune Bymiljøetaten",
    author_email="diako.k@gmail.com",
    license="Bym-developers",
    url="https://bitbucket.org/dkezri/bympythonframework",
    download_url="https://bitbucket.org/dkezri/bympythonframework/get/{}.tar.gz".format(
        currentVersion),
    keywords=['testing', 'integrationTesting', 'webapi testing'],
    packages=find_packages(exclude=['bymtesting.scripts', 'tests']),
    package_data={'': ['*.bat', '*.cfg', '*.info']},
    install_requires=['requests==2.12.4', 'yapf==0.14.0', 'grequests',
                      'pydash==4.0.3', 'jsonpickle==0.9.4', 'docker==2.4.2', 'xlrd', 'colored'],
    extras_require={'sys_platform==win32': 'pypiwin32'},
    entry_points={
        'console_scripts': [
            'setuptesting=bymtesting.setup_test_workplace:main',
            "cleanuptesting=bymtesting.setup_test_workplace:clean",
            "refactortesting=bymtesting.setup_test_workplace:refactor"
        ]
    },
    cmdclass={
        'clean': CleanUpCommand
    }
)
