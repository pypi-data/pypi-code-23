#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "media_editing",
        version          = "2018.02.26.1144",
        description      = "media editing",
        long_description = long_description(),
        url              = "https://github.com/wdbm/media_editing",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "media_editing"
                           ],
        install_requires = [
                           "docopt",
                           "moviepy",
                           "propyte",
                           "pymediainfo",
                           "shijian",
                           "technicolor"
                           ],
        scripts          = [
                           "images_to_video.py",
                           "Markdown_to_HTML.py",
                           "vidgif.py"
                           ],
        entry_points     = """
                           [console_scripts]
                           media_editing = media_editing:media_editing
                           """
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
