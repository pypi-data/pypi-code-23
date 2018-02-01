import os
from setuptools import find_packages, setup


NAME = 'woger'
DESCRIPTION = 'Workspace manager library'
URL = 'https://gitlab.com/grihabor/woger'
EMAIL = 'grihabor@mail.ru'
AUTHOR = 'Borodin Gregory'

REQUIRED = [
    'pathlib2',
]


def _get_project_path():
    return os.path.abspath(os.path.join(__file__, os.pardir))


def get_version():
    project_path = _get_project_path()
    init_path = os.path.join(project_path, NAME, '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                version_string = line.split('=')[-1].strip()
                return version_string.strip("'")


def get_readme():
    project_path = _get_project_path()
    readme_path = os.path.join(project_path, 'README.rst')
    with open(readme_path, 'r') as f:
        return f.read()


def main():
    setup(
        name=NAME,
        version=get_version(),
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        packages=find_packages(exclude=('tests',)),
        install_requires=REQUIRED,
        setup_requires=[
            'pytest-runner',
        ],
        tests_require=[
            'pytest',
            'pytest-cov',
        ],
        include_package_data=True,
        license='MIT',
        long_description=get_readme(),
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
        ],
        keywords='woger workspace manager directory structure version control'
    )


if __name__ == '__main__':
    main()
