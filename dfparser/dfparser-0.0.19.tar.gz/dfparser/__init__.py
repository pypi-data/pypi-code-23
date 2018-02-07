"""Init script.

Set package version.
"""
import os
import sys

from pkg_resources import get_distribution

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
if CUR_DIR not in sys.path:
    sys.path.append(CUR_DIR)
del CUR_DIR

from df_data import def_values
from df_data import type_codes
from envelope_parser import create_message
from envelope_parser import get_messages_from_stream
from envelope_parser import parse_from_file
from envelope_parser import parse_message
from envelope_parser import read_machine_header
from rsb_event_pb2 import Point
from rsh_parser import dump_to_rsb
from rsh_parser import parse_from_rsb
from rsh_parser import RshPackage
from rsh_parser import serialise_to_rsh
from rsh_parser import serialize_to_rsb

__version__ = get_distribution('dfparser').version
