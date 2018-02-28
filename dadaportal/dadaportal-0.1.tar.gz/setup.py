from distutils.core import setup

setup(name='dadaportal',
      author='Thomas Levine',
      author_email='_@thomaslevine.com',
      description='Dada management',
      url='https://thomaslevine.com/scm/dadaportal/',
      packages=['dadaportal',
                'dadaportal.render'],
      include_package_data=True,
      package_data = {
          'dadaportal.render': ['render/lib/*', 'render/templates/*'],
      },
      extras_require = {
          'check': 'requests>=2.13.0',
      },
      install_requires = [
          'horetu>=0.2',

          'lxml>=3.4.2',
          'Jinja2>=2.8',

          'docutils>=0.12',
          'Markdown>=2.6.1'
      ],
      tests_require = [
          'pytest>=2.6.4',
      ],
      version='0.1',
      license='AGPL',
      entry_points = {
          'console_scripts': ['dadaportal = dadaportal:dadaportal']
      },
)
