#!/usr/bin/python

import sys
import argparse
import datetime
if (sys.version_info > (3, 0)):
   from geomepy.geometry import *
   from geomepy.analysis import *
else:
   from geometry import *
   from analysis import *
import logging
import numpy as np

logging.basicConfig(filename='geomepy.log',level=logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def readxyz(fn):
   f = open(fn, 'r')
   lines=f.readlines()
   nat=int(lines[0])
   geom=Geometry()
   for line in lines[2:]:
      item=line.split()
      lbl=item[0]
      x=float(item[1])
      y=float(item[2])
      z=float(item[3])
      logging.debug("Adding atom from file {0} : {1} {2} {3} {4}".format(fn, lbl, x, y, z))
      geom.addAtom(lbl,x,y,z)
   return geom

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("-g", "--geoms", help="geometries to compare in xyz format", default="../tests/geom1.xyz ../tests/geom2.xyz")
   args = parser.parse_args()
#Default values
#
   geomfiles=args.geoms.split()
   geoms=[]
   for f in geomfiles:
      try:
         geom=readxyz(f)
      except:
         logging.critical("Cannot read {0} file".format(f))
         parser.print_help()
         sys.exit(1)
      geoms.append(geom)
   logging.info("Geometries read from files".format())
   for g in geoms:
      logging.info(g)
   geoms[0].center()
   geoms[1].center()
   logging.info("Geometries centered".format())
   for g in geoms:
      logging.info(g)
   compareGeoms(geoms[0], geoms[1])

if __name__ == '__main__':
    main()
