from setuptools import setup, find_packages
setup(name='dxl-wf',
      version='0.1.1',
      description='Workflow library.',
      url='https://github.com/Hong-Xiang/dxwf',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=['dxl.wf'],
      package_dir = {'': 'src/python'},
      install_requires=[],
      scripts=[],
      zip_safe=False)
