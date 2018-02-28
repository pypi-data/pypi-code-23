#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: binaryrepr.py
Author: David LAMOULLER
Email: dlamouller@protonmail.com
Github: https://github.com/dlamouller
Description: binaryrep is a utility to display position of the bits of a number.
"""

from __future__ import unicode_literals
import sys
from math import log
import click

#option fo click
click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


delim = lambda x, y: " " * x + y + " "

class BaseDepiction(object):
    """BaseDepiction"""

    def __init__(self, x, type_rep="bin", outformat="basic", short_repr=False, verbosity=False):
        super(BaseDepiction, self).__init__()
        try:
            if x.startswith('0x'):
                self.x = int(x, 16)
            elif x.startswith('0b'):
                self.x = int(x, 2)
            elif x.startswith('0'):
                self.x = int(x, 8)
            else:
                self.x = int(x)
        except ValueError as e:
            print("!!! Oups !!! {}".format(e))
            sys.exit()
        self.power = dict(hex=4, oct=3).get(type_rep, 1)
        self.outformat = outformat
        self.short_repr = short_repr
        self.verbosity = verbosity
        self.delimiter = "|"
        self.delimiterhead = "--|"
        if self.verbosity:
            self.reprpos = "position bits "
            self.reprbin = "value "
        else:
            self.reprpos = ""
            self.reprbin = ""
        self.depth = 7
        for d in filter(lambda e: round(log(self.x, 2) + 0.5) <= e, [8, 16, 32, 64, 128]):
            self.depth = d
            break
        if self.power == 4:
            self.x = format(self.x, 'x')
        elif self.power == 3:
            self.x = format(self.x, 'o')
        else:
            self.x = format(self.x, 'b')

        if not self.short_repr:
            self.x = int((self.depth/self.power - len(self.x) + 1)) * "0" + self.x
        if sys.byteorder == "little":
            nbbits = [i * self.power for i in range(len(self.x) -1, -1, -1)]
        else:
            nbbits = [i * self.power for i in range(len(self.x) -1)]
        self.position = list(map(str, nbbits))


    def __repr__(self):
        header = ""
        data   = ""

        if self.verbosity:
            print("endianness: {0}".format(sys.byteorder))
        adjustspace = len(self.reprpos) - len(self.reprbin)
        for s in self.position:
            header += s + delim(0, self.delimiter)
        header = self.reprpos + delim(0, self.delimiter) + header[:-1] + "\n"
        delimheader =""
        for p in self.position:
            if int(p) > 9: # when value greater than 1023
                delimheader += "-" + self.delimiterhead
                if self.outformat == "center":
                    delimheader = delimheader.replace("---|", ":-:|")
                elif self.outformat == "left":
                    delimheader = delimheader.replace("---|", ":--|")
                elif self.outformat == "right":
                    delimheader = delimheader.replace("---|", "--:|")
            else:
                delimheader += self.delimiterhead
        delimheader = "|" + delimheader + "\n"
        if self.verbosity:
            if self.outformat=="center":
                delimheader = "|:-:" + delimheader
            elif self.outformat=="left":
                delimheader = "|:--" + delimheader
            elif self.outformat=="right":
                delimheader = "|--:" + delimheader
            else:
                delimheader = "|---" + delimheader


        for p, x in zip(self.position, self.x):
            if int(p) > 9: 
                nbspace = 1
            else:
                nbspace = 0
            data += x + delim(nbspace, self.delimiter)
        data = self.reprbin + delim(adjustspace, self.delimiter) + data[:-1] + "\n"
        return header + delimheader + data


@click.command(context_settings=CONTEXT_SETTINGS, help="representation of a number in binary, hexadecimal or oct according to your system byteorder")
@click.option("-t", "--type_repr", default="bin", type=click.Choice(['bin', 'hex', 'oct']), help="type of representation of number, binary by default")
@click.option("-f", "--outformat", default="basic", type=click.Choice(['center', 'left', 'right', 'basic']), help="outpout format representation. basic by default")
@click.option("-s", "--short", is_flag=True, help="short representation")
@click.option("-v", "--verbose", is_flag=True, help="verbose mode")
@click.argument("value")
def binaryrepr(value, type_repr, outformat, short, verbose):
    if verbose:
        print("representation of {0}".format(value))
        print("{0}".format(BaseDepiction(value, type_repr, outformat, short, verbose)))
    else:
        print("{0}".format(BaseDepiction(value, type_repr, outformat, short, verbose)))


if __name__ == "__main__":
    binaryrepr()

