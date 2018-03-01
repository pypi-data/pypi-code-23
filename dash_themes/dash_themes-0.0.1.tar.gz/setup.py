from setuptools import setup

exec (open('dash_themes/version.py').read())

setup(
    name='dash_themes',
    version=__version__,
    author='plotly',
    packages=['dash_themes'],
    include_package_data=True,
    license='Commercial',
    description='Dash UI component suite',
    install_requires=[]
)
