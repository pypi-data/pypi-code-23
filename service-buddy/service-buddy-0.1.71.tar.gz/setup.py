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
        name = 'service-buddy',
        version = '0.1.71',
        description = 'CLI for managing micro-services',
        long_description = 'CLI for managing micro-services',
        author = '',
        author_email = '',
        license = 'Apache 2.0',
        url = 'https://github.com/AlienVault-Engineering/service-buddy',
        scripts = ['scripts/service-buddy'],
        packages = [
            'service_buddy',
            'service_buddy.ci',
            'service_buddy.code',
            'service_buddy.commands',
            'service_buddy.context',
            'service_buddy.service',
            'service_buddy.util',
            'service_buddy.vcs',
            'service_buddy.commands.bootstrap',
            'service_buddy.commands.clone',
            'service_buddy.commands.git',
            'service_buddy.commands.initialize',
            'service_buddy.commands.list'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {
            'service_buddy': ['code/builtin-code-templates.json']
        },
        install_requires = [
            'PyGithub',
            'cookiecutter',
            'pybitbucket',
            'click',
            'infra_buddy'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
