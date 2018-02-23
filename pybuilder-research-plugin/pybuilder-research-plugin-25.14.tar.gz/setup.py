#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'pybuilder-research-plugin',
        version = '25.14',
        description = '',
        long_description = '',
        author = 'Ingo Fruend',
        author_email = 'github@ingofruend.net',
        license = '',
        url = 'https://github.com/igordertigor/pybuilder-research-plugin',
        scripts = [],
        packages = ['pybuilder_research_plugin'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '!=3.0,!=3.1,!=3.2,>=2.7',
        obsoletes = [],
    )
