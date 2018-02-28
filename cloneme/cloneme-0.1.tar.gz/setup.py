from setuptools import setup, find_packages

setup(name='cloneme',
      version='0.1',
      description='A git clone wrapper to make cloning repos easier',
      keywords='git clone wrapper',
      url='http://github.com/LucianoFromTrelew/cloneme',
      author='Luciano Serruya Aloisi',
      author_email='lucianoserruya@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['*tests*']),
      python_requires='>=3',
      # install_requires=[
          # 'markdown',
      # ],
      entry_points={
          'console_scripts': ['cloneme=cloneme.cloneme:main'],
      },
  )
