from setuptools import setup, find_packages
setup(name='dxl-dxpy-dxfs',
      version='0.1.3',
      description='File system library.',
      url='https://github.com/Hong-Xiang/dxl',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=['dxl'],
      package_dir = {'': 'src/python'},
      install_requires=[
          'click',
          'rx',
      ],
      scripts=['src/cli/dxfs.py'],
      namespace_packages = ['dxl'],
      zip_safe=False)
