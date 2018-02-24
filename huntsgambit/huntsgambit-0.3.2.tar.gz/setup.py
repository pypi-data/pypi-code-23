from setuptools import setup


setup(
     name='huntsgambit',
     version='0.3.2',
     url="https://github.com/abel1311/hunts_gambit",
     packages=['huntsgambit'],
     entry_points={
        "console_scripts": ['is_pwnified = huntsgambit.is_pwnified:hunts_gambit']
        },
     install_requires=[
         'requests',
         'argparse',
         'pandas>=0.19.1'
     ]
)
