from ecscli import runCmd
from ecscli import main_parser
import common
import sys
import inspect

from test_common import *


def list_all(silent=False):
    sys.argv = ["", "vdc_data", "list"]
    result = runCmd()
    printit(result, silent)


def show_by_id(silent=False):
    sys.argv = ["", "vdc_data", "show", "-vdcId", "urn:storageos:VirtualDataCenterData:9fd74b65-3b97-4e10-bf6f-c82228caf273"]
    result = runCmd()
    printit(result, silent)

def show_by_name(silent=False):
    sys.argv = ["", "vdc_data", "show", "-name", "vdc2"]
    result = runCmd()
    printit(result, silent)
