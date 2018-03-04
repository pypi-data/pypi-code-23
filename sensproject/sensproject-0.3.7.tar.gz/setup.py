from setuptools import setup
import os

datafiles = [('sensproject/skel', ['sensproject/skel/.ccsproject', 'sensproject/skel/.cproject', 'sensproject/skel/.project', 'sensproject/skel/leproject.cpp', 'sensproject/skel/main.cpp']), ('sensproject/skel/.settings', ['sensproject/skel/.settings/org.eclipse.cdt.codan.core.prefs', 'sensproject/skel/.settings/org.eclipse.cdt.debug.core.prefs', 'sensproject/skel/.settings/org.eclipse.core.resources.prefs']), ('sensproject/skel/Debug', []), ('sensproject/skel/targetConfigs', ['sensproject/skel/targetConfigs/MSP430F2617.ccxml', 'sensproject/skel/targetConfigs/readme.txt'])]

setup(
    name = 'sensproject',
    packages = ['sensproject'],
    version = '0.3.7',
    description = 'A simple script to create new Senscape project',
    author = 'Guillem Castro',
    author_email = 'guillemcastro4@gmail.com',
    package_data={'sensproject': ['skel/*.cpp', 'skel/.project', 'skel/.cproject', 'skel/.ccsproject', 'skel/.settings/*', 'skel/Debug/*', 'skel/targetConfigs/*']},
    entry_points={
        'console_scripts': [
            'sensproj = sensproject.projectcreator:main',
        ],
    }
)