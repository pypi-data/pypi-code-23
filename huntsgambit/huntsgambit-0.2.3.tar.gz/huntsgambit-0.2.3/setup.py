from setuptools import setup
import re

# version = re.search(
#     '^__version__\s*=\s*"(.*)"',
#     open('huntsgambit/is_pwnified.py').read(),
#     re.M
#     ).group(1)

setup(
     name='huntsgambit',
     version='0.2.3',
     url="https://github.com/abel1311/hunts_gambit",
     entry_points={
        "console_scripts": ['is_pwnified = huntsgambit.is_pwnified:main']
        },
     install_requires=[
         'requests',
         'argparse',
         'pandas>=0.19.1'
     ]
)
