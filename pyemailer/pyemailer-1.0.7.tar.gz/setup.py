from setuptools import setup

setup(
    name='pyemailer',
    version='1.0.7',
    description='A very simple, generic, python emailer that can send plain text emails or tornado template driven emails. ',
    author='Eric Rosenzweig',
    author_email='rosenzweigit@gmail.com',
    py_modules=['pyemailer'],
    requires=['tornado'],
    keywords=['email', 'template']
)