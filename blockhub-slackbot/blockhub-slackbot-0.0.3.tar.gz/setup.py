from setuptools import setup

setup(
    name='blockhub-slackbot',
    version='0.0.3',
    packages=['slackbot'],
    url='https://github.com/blockhub/slackbot',
    license='MIT',
    author='Charles',
    author_email='karel@blockhub.nl',
    description='liteweight synchronous botframework for slack',
    install_requires=['slackclient']
)
