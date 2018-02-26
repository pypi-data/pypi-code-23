from setuptools import setup

setup(
    name='aztfgen',
    version='0.1.1',
    description='Generate terraform config from deployed azure resources.',
    long_description=open("README.md").read(),
    url='http://github.com/glenjamin/azure-terraform-generate',
    author='Glen Mailer',
    author_email='glen@stainlessed.co.uk',
    license='MIT',
    packages=['aztfgen', 'aztfgen.resources'],
    python_requires='>=3.5',
    zip_safe=False,
    entry_points = {
        'console_scripts': ['aztfgen=aztfgen:main'],
    }
)
