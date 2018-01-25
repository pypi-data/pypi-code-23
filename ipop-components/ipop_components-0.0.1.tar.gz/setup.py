from setuptools import setup

exec (open('ipop_components/version.py').read())

setup(
    name='ipop_components',
    version=__version__,
    author='rmarren1',
    packages=['ipop_components'],
    include_package_data=True,
    license='MIT',
    description='IPOP Portal component suite',
    install_requires=[]
)
