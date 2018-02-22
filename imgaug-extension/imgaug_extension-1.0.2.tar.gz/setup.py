from setuptools import setup, find_packages

setup(name='imgaug_extension',
      version='1.0.2',
      description="Extension package for imgaug",
      url='https://github.com/cadenai/imgaug_extension',
      download_url = 'https://github.com/cadenai/imgaug_extension/archive/1.0.tar.gz',
      author='caden.ai',
      author_email='info@caden.ai',
      packages=find_packages(),
      install_requires=["imgaug", "numpy", "scikit-image>=0.13.1"]
      )