try:
    from setuptools import setup
except ImportError:
    # can't have the entry_points option here.
    from distutils.core import setup

setup(name='dotman',
      version='1.2.0',
      author="Ahmed T. Youssef",
      author_email="xmonader@gmail.com",
      description='Manage your dotfiles easily.',
      long_description='Manage your dotfiles easily',
      packages=['dotman'],
      scripts=['scripts/dotman'],
      url="http://github.com/xmonader/dotman",
      license='BSD 3-Clause License',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      )
