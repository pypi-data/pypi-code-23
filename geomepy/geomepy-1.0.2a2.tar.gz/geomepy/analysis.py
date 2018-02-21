#!/usr/bin/python

import sys
import logging
import numpy as np
if (sys.version_info > (3, 0)):
   import geomepy.geometry
else:
   import geometry
import math
from pyquaternion import Quaternion

def compareGeoms(geom1, geom2):
   x=geom1.getCoords()
   y=geom2.getCoords()
   logging.debug("coordsx {0}".format(x))
   logging.debug("coordsy {0}".format(y))
   R=np.matrix('0.0 0.0 0.0 ; 0.0 0.0 0.0 ; 0.0 0.0 0.0')
   xnorm2=0.0
   ynorm2=0.0
   N=len(x)
   for k in range(N):
      xnorm2 += np.dot(x[k],x[k])
      ynorm2 += np.dot(y[k],y[k])
      for i in range(3):
         for j in range(3):
            R[i,j] += x[k][i] * y[k][j]
   logging.debug("R matrix :\n{0}".format(R))
   F=np.matrix('0.0 0.0 0.0 0.0 ; 0.0 0.0 0.0 0.0 ; 0.0 0.0 0.0 0.0 ; 0.0 0.0 0.0 0.0')
   F[0,0] = R[0,0] + R[1,1] + R[2,2]
   F[0,1] = R[1,2] - R[2,1]
   F[0,2] = R[2,0] - R[0,2]
   F[0,3] = R[0,1] - R[1,0]
#
   F[1,0] = F[0,1]
   F[1,1] = R[0,0] - R[1,1] - R[2,2]
   F[1,2] = R[0,1] + R[1,0]
   F[1,3] = R[0,2] + R[2,0]
#
   F[2,0] = F[0,2]
   F[2,1] = F[1,2]
   F[2,2] =-R[0,0] + R[1,1] - R[2,2]
   F[2,3] = R[1,2] + R[2,1]
#
   F[3,0] = F[0,3]
   F[3,1] = F[1,3]
   F[3,2] = F[2,3]
   F[3,3] =-R[0,0] - R[1,1] + R[2,2]

   eigv, eigf = np.linalg.eig(F)
   logging.debug("Eigenvalues :\n{0}".format(eigv))
   logging.debug("Eigenfunctions :\n{0}".format(eigf))
   l_max = max(eigv)
   q = Quaternion(eigf[:,0])
   logging.debug("Quaternion :\n{0}".format(q))
   rotation = q.rotation_matrix
   logging.debug("Rotation matrix :\n{0}".format(rotation))
   RMSD = math.sqrt((xnorm2+ynorm2-2.0*l_max)/(1.0*N))
   logging.info("RMSD {0}".format(RMSD))
   return RMSD, rotation
   

def main():
   print('analysis module')

if __name__ == '__main__':
   main()
