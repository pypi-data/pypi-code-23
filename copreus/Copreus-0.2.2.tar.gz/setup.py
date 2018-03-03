from setuptools import setup, find_packages
import os
import copreus.drivers
import copreus

def get_console_scripts():
    scripts = [
        'copreus = copreus.devicemanager.devicemanager:standalone',
        'copreus_devicemanager = copreus.devicemanager.devicemanager:standalone',
    ]

    drivers = copreus.drivers.get_drivers()
    for k, driver in drivers.items():
        script_name = "copreus_" + (driver["name"]).lower()
        script = driver["module"] + ":standalone"
        scripts.append(script_name + " = " + script)

    return scripts


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if os.path.isfile(os.path.join(os.path.dirname(__file__), 'README.md')):
    from pypandoc import convert
    readme_rst = convert(os.path.join(os.path.dirname(__file__), 'README.md'), 'rst')
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'w') as out:
        out.write(readme_rst + '\n')

setup(
    name='Copreus',
    version=copreus.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README.rst'),
    description='This library provides a framework to write device drivers for the raspberry pi that are connected to MQTT.',
    url='https://gitlab.com/pelops/copreus/',
    author='Tobias Gawron-Deutsch',
    author_email='tobias@strix.at',
    keywords='mqtt device driver rpi raspberry pi',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.5',
    install_requires=[
        "paho-mqtt",
        "pyyaml",
        "RPi.GPIO"
    ],
#    dependency_links=[
#        adc - spidev
#        bme280 - smbus2, bme280
#        dac - spidev
#        dht - Adafruit_DHT
#        epaper - spidev, Pillow (...)
#        input - nix
#        output - nix
#        rotaryencoder - nix
#    ],
    entry_points={
        'console_scripts': get_console_scripts()
    },

)
