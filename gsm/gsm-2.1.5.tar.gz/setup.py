from setuptools import setup

setup(name='gsm'
     ,version='2.1.5'
     ,description="LOFAR's Global Sky Model (GSM)"
     ,url='https://github.com/bartscheers/gsm'
     ,author='Bart Scheers'
     ,author_email='bartscheers@gmail.com'
     ,packages=['gsm']
     ,scripts=['bin/gsm']
     ,install_requires=['numpy', 'six', 'pymonetdb', 'matplotlib']
     ,include_package_data=True
     ,zip_safe=False
     )

