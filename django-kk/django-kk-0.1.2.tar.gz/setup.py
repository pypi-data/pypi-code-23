import os
import kk
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

CLASSIFIERS = [
#    Development Status :: 1 - Planning
#    Development Status :: 2 - Pre-Alpha
#    Development Status :: 3 - Alpha
#    Development Status :: 4 - Beta
#    Development Status :: 5 - Production/Stable
#    Development Status :: 6 - Mature
#    Development Status :: 7 - Inactive
    'Development Status :: 3 - Alpha',

#    Environment :: Console
#    Environment :: Console :: Curses
#    Environment :: Console :: Framebuffer
#    Environment :: Console :: Newt
#    Environment :: Console :: svgalib
#    Environment :: Handhelds/PDA's
#    Environment :: MacOS X
#    Environment :: MacOS X :: Aqua
#    Environment :: MacOS X :: Carbon
#    Environment :: MacOS X :: Cocoa
#    Environment :: No Input/Output (Daemon)
#    Environment :: OpenStack
#    Environment :: Other Environment
#    Environment :: Plugins
#    Environment :: Web Environment
#    Environment :: Web Environment :: Buffet
#    Environment :: Web Environment :: Mozilla
#    Environment :: Web Environment :: ToscaWidgets
#    Environment :: Win32 (MS Windows)
#    Environment :: X11 Applications
#    Environment :: X11 Applications :: Gnome
#    Environment :: X11 Applications :: GTK
#    Environment :: X11 Applications :: KDE
#    Environment :: X11 Applications :: Qt
    'Environment :: Web Environment',

#    Framework :: Flask
    'Framework :: Django',
    'Framework :: Django :: 2.0',

    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',

#    'Natural Language :: English',
    'Natural Language :: Russian',


    'Operating System :: OS Independent',

    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',

    'Topic :: Software Development :: Libraries',
]

INSTALL_REQUIREMENTS = [
    'Django>=2.0,<3.0',
    'django-ckeditor>=5.3,<6',
    'Pillow>=5',
    'PyYAML>=3.12,<4',
    #'Markdown2>=2.3,<3',
    'sorl-thumbnail>=12.4.1,<13'
]

setup(
    name = 'django-kk',
    version = kk.__version__,

    license = 'MIT',
    description = 'Kenzo Kit for Django.',
    long_description = README,

    author = 'icw82',
    author_email = 'icw82@yandex.ru',
    url = 'https://icw82.ru/',

    packages = find_packages(),
    include_package_data = True,

    classifiers = CLASSIFIERS,
    keywords = 'REST API JSON',
    install_requires = INSTALL_REQUIREMENTS,
)
