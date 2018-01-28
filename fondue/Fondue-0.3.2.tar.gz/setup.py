from setuptools import setup

from fondue import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name='Fondue',
      version=__version__,
      description='A Python program for connecting peers on a virtual LAN, performing NAT punchthrough if needed.',
      long_description=long_description,
      author='Ariel Antonitis',
      author_email='arant@mit.edu',
      #url='https://github.com/arantonitis/wallop', TODO
      packages=['fondue'],
      entry_points={'console_scripts': ['fondue = fondue.client:main', 'fondue-server = fondue.server:main',
                                        'fondue-test-send = fondue.test_send:main',
                                        'fondue-test-recv = fondue.test_recv:main',
                                        'fondue-chat = fondue.chat:main']},
      license='MIT',
      classifiers=['License :: OSI Approved :: MIT License'],
      python_requires='>=3'
      )
