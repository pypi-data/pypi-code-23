from distutils.core import setup
setup(
  name = 'ybc_animal',
  packages = ['ybc_animal'],
  package_data = {'ybc_animal':['data/*']},
  version = '2.0.0',
  description = 'Recognition Image Animal',
  long_description='Recognition Image Animal',
  author = 'KingHS',
  author_email = '382771946@qq.com',
  keywords = ['pip3', 'python3','python','Recognition Image Animal'],
  license='MIT',
  install_requires=['requests']
)
