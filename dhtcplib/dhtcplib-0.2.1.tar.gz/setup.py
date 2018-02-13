"""
Dhtcplib
--------

dhtcplib makes threaded TCP servers and connections to servers really easy.

```````````````

::

from time import sleep
from dhtcplib import dhtcp

'''
	Start the server
'''
class MyHandlerClass:
    def handle(data):
        print("Handler got data: ", data)
        return(data)

# Using a defined class with a 'handle' method to route requests 
my_serv = dhtcp("127.0.0.1", 9000, RouterClass=MyHandlerClass)
my_serv.start()

try:
    while True:
        print("Do something in your main thread while the server slaves away!")
        sleep(5)

except KeyboardInterrupt:

    '''
        Shutdown the server
    '''
    my_serv.kill()


And Easy to Install
```````````````````

::

    $ pip3 install dhtcplib


"""

from distutils.core import setup

setup(name = "dhtcplib",
    version="0.2.1",
    description="A simple TCP client/server framework",
    author="Josh Bosley",
    author_email="bosley117@gmail.com",
    license="MIT",
    url="https://github.com/DigitalHills/TCP-CommUnit",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: System :: Monitoring" ],
    packages=['dhtcplib'])

