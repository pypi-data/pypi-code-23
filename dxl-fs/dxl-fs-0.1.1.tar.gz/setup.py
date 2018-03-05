from setuptools import setup, find_packages
setup(name='dxl-fs',
      version='0.1.1',
      description='File system library.',
      url='https://github.com/Hong-Xiang/dxl',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=['dxl.fs'],
      package_dir = {'': 'src/python'},
      install_requires=[
          'click',
          'rx',
      ],
      scripts=['src/cli/dxfs.py'],
    #   namespace_packages = ['dxl'],
      zip_safe=False)
