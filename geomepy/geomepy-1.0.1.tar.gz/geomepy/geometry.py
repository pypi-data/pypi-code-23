#!/usr/bin/python

import logging
from elements import elements
import elements.elements as elements
import numpy as np

class Geometry:
   def __init__(self, geom=None):
      if geom==None:
         self.geom={}
      else:
         self.geom=geom

   def __str__(self):
      nat=len(self.geom)
      val="{0} atoms\n\n".format(nat)
      for k in self.geom.keys():
         val += str(self.geom[k])+'\n'
      val+="\nCenter of mass : {0}".format(self.getCenterofMass())
      return val

   def addAtom(self, lbl, x, y, z):
      nat=len(self.geom)
      self.geom[str(nat)]=Atom(lbl, np.array([x,y,z]))

   def getGeom(self):
      return self.geom

   def getCoords(self):
      val = [ (self.geom[k]).getPos() for k in self.geom.keys() ]
      return val

   def center(self):
      x_av = np.average([ self.geom[k].getPos()[0] for k in self.geom.keys() ])
      y_av = np.average([ self.geom[k].getPos()[1] for k in self.geom.keys() ])
      z_av = np.average([ self.geom[k].getPos()[2] for k in self.geom.keys() ])
      orig = np.array([ x_av, y_av, z_av ])
      for k in self.geom.keys():
         self.geom[k].move(-orig)

   def getCenterofMass(self):
      pos=np.array([0.,0.,0.])
      tot=0.0
      for k in self.geom.keys():
         a = self.geom[k]
         mass = float(a.getMass().split()[0])
         mass=1.0
         tot += mass
         pos += mass*a.getPos()
      logging.info("Total mass: {0}".format(tot))
      return pos/tot

   def translateTo(self, geomRef):
      delta=geomRef.getCenterofMass()-self.getCenterofMass()
      logging.info("DELTA = {0}".format(delta))
      for k in self.geom.keys():
         self.geom[k].pos += delta

class Atom:
   def __init__(self, lbl, pos):
      self.lbl=lbl
      self.pos=pos

   def __str__(self):
      val="{0}\t{1}\t{2}\t{3}".format(self.lbl, self.pos[0], self.pos[1], self.pos[2])
      return val
   
   def getPos(self):
      return self.pos

   def move(self, v):
      self.pos += v

   def getLabel(self):
      return self.lbl

   def getMass(self):
      data = elements.__dict__[self.getLabel()]
      return data.AtomicMass

def main():
   print (elements.Table)

if __name__ == '__main__':
   main()
