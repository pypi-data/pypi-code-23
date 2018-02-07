from setuptools import setup

setup(name='FunctionScaler',
      version='0.1',
      description='Given a discrete probability density function learn a function that turns samples from the pdf into samples from desired distribution.',
      url='https://github.com/weissercn/FunctionScaler',
      author='Constantin Weisser',
      author_email='weissercn@gmail.com',
      license='MIT',
      packages=['FunctionScaler'],
      install_requires=[
          'numpy',
          'scipy',
      ],
      zip_safe=False)
