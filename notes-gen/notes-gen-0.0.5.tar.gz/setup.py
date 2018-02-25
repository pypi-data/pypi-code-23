from setuptools import setup
from setuptools import find_packages

setup(name='notes-gen',
      version='0.0.5',
      description='A static site generator for markdown notes.',
      url='https://github.com/sunitdeshpande/notes-gen',
      author='Sunit Deshpande',
      author_email='sunitdeshpande1234@gmail.com',
      license='WTFPL',
      packages=find_packages(),
      package_data={
          'notes_gen': ['template/**/*', 'template/_config.json'],
      },
      python_requires='>=3',
      keywords='notes generator static site',
      install_requires=[
          'networkx',
          'python-slugify',
          'Jinja2',
          'beautifulsoup4',
      ],
      entry_points={
          'console_scripts': ['notes-gen=notes_gen.command_line:main'],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Topic :: Education',
          'Topic :: Software Development :: Documentation',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ])
