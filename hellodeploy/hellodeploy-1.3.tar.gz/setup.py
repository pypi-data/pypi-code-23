from setuptools import setup

setup(
    name='hellodeploy',    # This is the name of your PyPI-package.
    version='1.3',           # Update the version number for new releases
    entry_points = {
        "console_scripts": ['hellodeploy = hellodeploy.cli:main']
    },
    url='https://github.com/quantfive/hellodeploy-cli',
    author='Itai Reuveni',
    author_email='itaireuveni@gmail.com',
    license='MIT',
    packages=['hellodeploy'],
    zip_safe=False
)
