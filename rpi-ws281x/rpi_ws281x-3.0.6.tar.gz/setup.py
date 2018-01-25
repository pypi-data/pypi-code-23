#!/usr/bin/env python
# Python wrapper for the rpi_ws281x library.
# Authors:
#    Phil Howard (phil@pimoroni.com) 
#    Tony DiCola (tony@tonydicola.com)

from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
import subprocess

class CustomInstallCommand(build_py):
    """Customized install to run library Makefile"""
    def run(self):
        print("Compiling ws281x library...")
        proc =subprocess.Popen(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(proc.stderr.read())
        build_py.run(self)

setup(name              = 'rpi_ws281x',
      version           = '3.0.6',
      author            = 'Jeremy Garff <jer@jers.net>, Phil Howard <phil@pimoroni.com>',
      author_email      = 'jer@jers.net',
      description       = 'Userspace Raspberry Pi PWM/PCM/SPI library for SK6812 and WS281X LEDs.',
      license           = 'MIT',
      url               = 'https://github.com/pimoroni/rpi_ws281x-python/',
      cmdclass          = {'build_py':CustomInstallCommand},
      packages          = ['neopixel', 'rpi_ws281x'],
      ext_modules       = [Extension('_rpi_ws281x', 
                                     sources=['rpi_ws281x_wrap.c'],
                                     include_dirs=['lib/'],
                                     library_dirs=['lib-built/'],
                                     libraries=['ws2811'])])
