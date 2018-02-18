from setuptools import setup

setup(
    name='helpdeskbot',
    version='1.0.4',
    description='Discord utility bot for DevDungeon.com',
    url='https://github.com/DevDungeon/HelpDeskBot',
    author='DevDungeon',
    author_email='nanodano@devdungeon.com',
    license='GPL-3.0',
    packages=['helpdeskbot'],
    scripts=[
        'bin/helpdeskbot',
        'bin/helpdeskbot.bat',
    ],
    zip_safe=False,
    install_requires=[
        'discord.py',
        'docopt',
        'aiohttp',
    ]
)
