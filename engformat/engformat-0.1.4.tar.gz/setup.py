from setuptools import setup

setup(name='engformat',
      version='0.1.4',
      description='Tools for displaying engineering calculations according to the Engineering Standard Format',
      url='',
      author='Maxim Millen',
      author_email='millen@fe.up.pt',
      license='MIT',
      packages=[
        'engformat',
    ],
    install_requires=[
        "numpy",
        "bwplot>=0.2.10",
        "sfsimodels"
    ],
      zip_safe=False)