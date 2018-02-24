__version__ = '1.0.1'
__author__ = "ysharma"

""" 

Setting Text ForeGround Color. This can be used with Print Statement.
Ref: blender build scripts

Eg: 

Python3.x:

import bcolors as b
print(b.OK + "Color Statement" + b.END)


Python2.x:

import bcolors as b
print b.OK + "Color Statement" + b.END


"""

OK = '\033[92m'
WARN = '\033[93m'
UNDERLINE = '\033[4m'
ITALIC = '\x1B[3m'
BOLD = '\033[1m'
ENDC = '\033[0m'
BLUE = '\033[94m'

HEADER = '\033[95m' + BOLD
PASS = '\033[92m' + BOLD
FAIL = '\033[91m' + BOLD

OKMSG = BOLD + OK + u'\u2705' + "  "
ERR = BOLD + FAIL + u"\u274C" + "  "
WAIT = BOLD + WARN + u'\u231b' + "  "

HELP = WARN
BMSG = BOLD + OK

BITALIC = BOLD + ITALIC
BLUEIC = BITALIC + OK
END = ENDC