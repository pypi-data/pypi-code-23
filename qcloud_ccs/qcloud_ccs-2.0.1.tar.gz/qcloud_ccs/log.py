#!/usr/bin/env python3

import sys
import logging

#logging.basicConfig()
log = logging.getLogger('CCS')
log.setLevel(logging.INFO)

stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(logging.Formatter("[%(levelname)-5s][%(asctime)s][%(filename)s:%(lineno)d] %(message)s", "%d %b %Y %H:%M:%S"))
log.addHandler(stdout)