import sys
import configparser
from mtbparser import snv_utils
from .mtbconverter import MtbConverter
from .argparser import *
from .utils import getbarcode
from zipfile import ZipFile
from .cx_controlled_vocabulary import ControlledVocabulary
from .cx_parameters import Parameters
from .cx_profiles import *
from .cx_connect import CXXConnect
from .mtbconverter_exceptions import ParseConfigFileException
from requests.exceptions import ConnectTimeout

__version__ = "0.1.1"

COMMANDS = ['convert', 'push', 'catalogue']


def main(args=None):
    """The main routine, parsing arguments and calls the converter"""
    print("Mtbconverter version {}.".format(__version__))

    if args is None:
        args = sys.argv
    if len(args) < 2:
        print(help_message())
        sys.exit(1)
    if args[1] not in COMMANDS:
        print(help_message())
    if args[1] == 'convert':
        parser = conversion_parser()
        start_conversion(parser.parse_args(args[2:]))
    if args[1] == 'catalogue':
        build_catalogue()
    if args[1] == 'push':
        parser = push_parser()
        push(parser.parse_args(args[2:]))
    sys.exit(0)


def push(args):
    """Establish a connection to CentraXX and tries to
    import a given XML file."""
    config = configparser.ConfigParser()
    config.read(args.c)
    
    if not config.sections():
        raise ParseConfigFileException('No sections found in the config!')

    section = 'CENTRAXX'
    if args.test: section = 'CENTRAXX_TEST'

    cxxconnect = CXXConnect(**config[section])

    if args.check: 
        try:
            response = cxxconnect.check()
            print(response)
        except ConnectTimeout:
            print("[ERROR]: The connection timed out.")
            sys.exit(1)
        sys.exit(0)
        
    cxxconnect.check()
     

def start_conversion(args):
    """Starts the file extraction, parsing and writes the
    output in an XML file."""
    path_zipfile = args.archive
    patient_code = args.patientID
    sample_code = getbarcode(path_zipfile)
    converter = MtbConverter(ZipFile(path_zipfile), sample_code=sample_code,
        patient_code=patient_code)
    converter.convert()


def build_catalogue():
    """Builds the XML catalogue for CentraXX according to the 
    file header specifications"""
    cv = ControlledVocabulary()
    params = Parameters()
    ssnv_profile = SSNVProfiles()
    gsnv_profile = GSNVProfiles()
    scnv_profile = SCNVProfiles()
    gcnv_profile = GCNVProfiles()
    sv_profile = SVProfiles()
    metadata_profile = MetadataProfiles()

    with open('cv_centraxx.xml', 'w') as output:
        output.write(cv.getXML().decode('utf-8'))
    with open('params_centraxx.xml', 'w') as output:
        output.write(params.getXML().decode('utf-8'))
    with open('ssnv_profiles_centraxx.xml', 'w') as output:
        output.write(ssnv_profile.getXML().decode('utf-8'))
    with open('gsnv_profiles_centraxx.xml', 'w') as output:
        output.write(gsnv_profile.getXML().decode('utf-8'))
    with open('scnv_profiles_centraxx.xml', 'w') as output:
        output.write(scnv_profile.getXML().decode('utf-8'))
    with open('gcnv_profiles_centraxx.xml', 'w') as output:
        output.write(gcnv_profile.getXML().decode('utf-8'))
    with open('sv_profiles_centraxx.xml', 'w') as output:
        output.write(sv_profile.getXML().decode('utf-8'))
    with open('metadata_profiles_centraxx.xml', 'w') as output:
        output.write(metadata_profile.getXML().decode('utf-8'))
    

def help_message():
    """Builds the string for the help message"""
    msg = "Usage: mtbconverter.py [-h] [command]\n\n"\
    "command:\n"\
    "\tconvert\t\tConverts variant information into CentraXX XML.\n"\
    "\tpush\t\tPushes one ore more XML files to CentraXX.\n"\
    "\tcatalogue\tBuilds CentraXX catalogue XML files."
    return msg

if __name__ == "__main__":
    main()
