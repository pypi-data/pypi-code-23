from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as req_file:
    requires = [req for req in req_file.read().split('\n') if req]

with open('requirements-dev.txt') as req_file:
    requires_dev = [req for req in req_file.read().split('\n') if req]

with open('VERSION') as fp:
    version = fp.read().strip()

setup(name='molo.yourwords',
      version=version,
      description=('A Molo module that enables user generated content '
                   'competitions'),
      long_description=readme,
      classifiers=[
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Framework :: Django",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Praekelt Foundation',
      author_email='dev@praekelt.com',
      url='http://github.com/praekelt/molo.yourwords',
      license='BSD',
      keywords='praekelt, mobi, web, django',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['molo'],
      install_requires=requires,
      tests_require=requires_dev,
      entry_points={})
