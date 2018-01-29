from setuptools import setup

setup(name='kinton',
      version='0.1',
      description='Kinton',
      keywords='ansible infrastructure provisioning',
      url='https://github.com/thecocktail/kinton',
      author='Jesus Sayar',
      author_email='jesus.sayar@the-cocktail.com',
      license='MIT',
      packages=['kinton'],
      install_requires=[
          'PyYAML==3.12',
          'ipdb==0.10.3',
          'termcolor==1.1.0',
          'pygithub==1.35',
          'Jinja2==2.9.6'
      ],
      entry_points = {
        'console_scripts': ['kinton=kinton.command_line:main'],
      },      
      include_package_data=True,
      zip_safe=False)
