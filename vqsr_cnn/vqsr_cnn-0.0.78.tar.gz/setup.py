from distutils.core import setup

setup(name='vqsr_cnn',
      version='0.0.78',
      description='Variant quality score recalibration with Convolutional Neural Networks',
      author='Sam Friedman',
      author_email='sam@broadinstitute.org',
      packages=['vqsr_cnn'],
      url='https://broadinstitute.org/',
      install_requires=[
          "keras >= 2.0",
          "numpy >= 1.13.1",
          "scipy >= 0.19.1"
      ]
      )
