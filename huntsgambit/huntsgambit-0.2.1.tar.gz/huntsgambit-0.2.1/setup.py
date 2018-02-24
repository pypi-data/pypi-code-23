from setuptools import setup

setup(
     name='huntsgambit',
     version='0.2.1',
     url="https://github.com/abel1311/hunts_gambit",
     entry_points={
        "console_scripts": ['is_pwnified = huntsgamble.is_pwnified:main']
        },
     install_requires=[
         'requests',
         'argparse',
         'pandas>=0.19.1'
     ]
)
