"""Argument parser collection for conversion
and pushing to CentraXX"""

import argparse

def conversion_parser():
    parser = argparse.ArgumentParser(prog="convert", description="Conversion of "
    "variant information into CentraXX schema conform XML.")
    parser.add_argument('archive' , help='ZIP archive containing the variant information files.')
    parser.add_argument('patientID' , help='A QBiC patient ID.')
    return parser

def push_parser():
    parser = argparse.ArgumentParser(prog="push", description="Import a converted XML file "
    "into CentraXX.")
    parser.add_argument('-c', metavar="config", default="/etc/centraxx.config", help='Configuration file with settings for the remote CentraXX system. (Default: /etc/centraxx.config)')
    parser.add_argument('-t', '--test', action='store_true', help='Import to the CentraXX test system.')
    parser.add_argument('--check', action='store_true', help='Check the connection to CentraXX.')
    parser.add_argument('patientdata', help='Converted XML file from an MTB ZIP archive with the variant information.')
    return parser