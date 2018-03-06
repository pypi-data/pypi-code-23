from setuptools import setup

exec (open('dash_renderer/version.py').read())

setup(
    name='dash-renderer-grasia',
    version=__version__,
    author='Akronix',
    packages=['dash_renderer'],
    include_package_data=True,
    license='MIT',
    description='Front-end component renderer for dash',
    install_requires=[]
)
