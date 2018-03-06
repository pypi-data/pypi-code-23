from distutils.core import setup
setup(
  name = 'ybc_face',
  packages = ['ybc_face'],
  # package_data = {'ybc_face':['data/*']},
  version = '4.0.6',
  description = 'Face Recognition And Desc Face Info',
  long_description='Face Recognition And Desc Face Info',
  author = 'KingHS',
  author_email = '382771946@qq.com',
  keywords = ['pip3', 'python3','python','Face Info'],
  license='MIT',
  # install_requires=['requests','opencv-python','pillow']
  install_requires=['requests','pillow']
)
