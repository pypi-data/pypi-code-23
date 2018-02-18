# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Functions for parallel computations on a single multi core machine using the standard library multiprocessing.

Not the programming details, but the way how to speed up some things.

This is no magic and just for convenience for non specialist of parallel computing.
The main thing is to pass additional parameters to the processes (a pool of workers)
and loop only over one parameter in the list to loop over. Opening and closing of the pool is hidden in the function.
In this way we can use a multicore machine with all cpus.

In some test i found that shared memory (sharedmemory ala Sturla Molden) does not really speed up,
if we just want to calculate a function e.g. for a list of different Q values.
Here the pickling of numpy arrays is efficient enough compared to the computation we do.
We use here only non modified input data and return a new dataset , so we dont need to care about 
what happens if one process changes the data needed in another process (race conditions,...).
Please keep in mind and dont complain if you modify input data.

- If your computation is faster than the communication (pickling and sending of data) then you dont need this module.
- If you want to use a cluster with all cpus, this is not the way.

For easier debugging (to find the position of an error in the pdb debugger) use the option debug.
In this case the multiprocessing is not used and the debugger finds the error correctly.


"""
from __future__ import print_function
from __future__ import division

import scipy.constants as constants
import multiprocessing as mp
import numpy as np

_Nrand=np.random.random_integers

def randomPointsN(NN,r=1):
    """
    N nearly random points on sphere of radius r based on golden ratio.
    
    Parameters
    ----------
    NN : int
        number of points
    r : float
        radius of sphere

    Returns
    -------
    array of [r,phi,theta]  pairs in radians

    """
    return np.c_[(r*np.ones(int(NN)),
                  np.mod((2*np.pi*_Nrand(-int(NN*1037),int(NN*1037),int(NN))/constants.golden)+np.pi,2*np.pi)-np.pi,
                  np.arcsin(2*_Nrand(-int(NN*1037),int(NN*1037),int(NN))/(2*int(NN*1037)+1.))+np.pi/2)]


def fibonacciLatticePointsOnSphere(NN, r=1):
    """
    Fibonacci lattice points on a sphere with radius r (default r=1)

    This can be used to integrate efficiently over a sphere with well distributed points.

    Parameters
    ----------
    NN : integer
        number of points = 2*N+1
    r : float, default 1
        radius of sphere

    Returns
    -------
    list of [r,phi,theta]  pairs in radians
        phi  azimuth -pi<phi<pi; theta polar angle  0<theta<pi

    References
    ----------
    .. [1] Measurement of Areas on a Sphere Using Fibonacci and Latitude–Longitude Lattices
          Á. González Mathematical Geosciences 42, 49-64 (2009)

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[1]>0) & (a[1]<np.pi/2) & (a[2]>0) & (a[2]<np.pi/2),points))
     pxyz=js.formel.rphitheta2xyz(pp)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)

     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[2]>0.3) & (a[2]<1) ,points))
     v=js.formel.rphitheta2xyz(pp)
     R=js.formel.rotationMatrix([1,0,0],np.deg2rad(-30))
     pxyz=np.dot(R,v.T).T
     #points in polar coordinates
     prpt=js.formel.xyz2rphitheta(np.dot(R,pxyz.T).T)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_aspect("equal")
     ax.set_xlabel('x')
     ax.set_ylabel('y')
     ax.set_zlabel('z')
     plt.tight_layout()
     plt.show(block=False)

    """
    return np.c_[(r * np.ones(2 * NN + 1),
                  np.mod((2 * np.pi * np.r_[-NN:NN + 1] / constants.golden) + np.pi, 2 * np.pi) - np.pi,
                  np.arcsin(2 * np.r_[-NN:NN + 1] / (2 * NN + 1.)) + np.pi / 2)]


def rphitheta2xyz(RPT):
    """
    Transformation  spherical coordinates [r,phi,theta]  to cartesian coordinates [x,y,z]
    
    Parameters
    ----------
    RPT : array Nx3
        | dim Nx3 with [r,phi,theta] coordinates
        | r     : float       length
        | phi   : float   azimuth     -pi < phi < pi
        | theta : float   polar angle  0 < theta  < pi

    Returns
    -------
    Array with same dimmension as RPT.

    """
    rpt=np.array(RPT,ndmin=2)
    xyz=np.zeros(rpt.shape)
    xyz[:,0]=rpt[:,0]*np.cos(rpt[:,1])*np.sin(rpt[:,2])
    xyz[:,1]=rpt[:,0]*np.sin(rpt[:,1])*np.sin(rpt[:,2])
    xyz[:,2]=rpt[:,0]*np.cos(rpt[:,2])
    return np.array(xyz.squeeze(),ndmin=np.ndim(RPT))


# noinspection PyIncorrectDocstring
def psphereAverage(funktion, relError=300, *args, **kwargs):
    """
    Parallel evaluation of spherical average of function.
    
    A fibonacci lattice on sphere is used.
    
    Parameters
    ----------
    funktion : function
        function to evaluate
        function first argument gets cartesian coordinate [x,y,z] of point on unit sphere
    relError : float, default 300
        | determines how points on sphere are selected
        | >1  Fibonacci Lattice with relError*2+1 points
        | <1  random points on sphere (Monte Carlo integration)
        |     stops if error is below relError
        |     Error is (stddev of N points) /(mean of N points)/sqrt(N)
    arg,kwargs : 
        forwarded to function
    
    Returns
    -------
    array like with values from function and appended error

    Notes
    -----
     - Works also on single core machines.
     - For integration over a continous function as a form factor in scattering the random points are not statistically
       independent. Think of neigbouring points on an isosurface which are correlated and therefore the standard deviation is biased..
       In this case the Fibonacci lattice is the better choice as the standard deviation in a random sample is not a measure of error
       but more a measure of the differneces on the isosurface.

    Examples
    --------
    ::

     def f(x,r):
        return [js.formel.xyz2rphitheta(x)[1:].sum()*r]
     js.parallel.psphereAverage(f,relError=500,r=1)


    """    
    if relError<0:
        relError=abs(relError**-2)
    if 'ncpu' in kwargs:
        ncpu=kwargs['ncpu']
        del kwargs['ncpu']
    else:
        ncpu=mp.cpu_count()
    pool = mp.Pool(ncpu)
    npoints=ncpu*20
    if 0 < abs(relError) < 1:
        points=rphitheta2xyz(randomPointsN(ncpu))
        jobs=[pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
        result=[np.asarray(job.get(0xFFFF)) for job in jobs]
        while 1:
            points=rphitheta2xyz(randomPointsN(npoints))
            jobs=[pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
            result+=[np.asarray(job.get(0xFFFF)) for job in jobs]
            results=np.array(result)
            if abs(results[:,0].std()/results[:,0].mean()/np.sqrt(np.shape(results[:,0])[0]))<relError and np.shape(results[:,0])[0]>42:
                print(np.shape(results[:, 0])[0], '  random points')
                break
    elif relError >1:
        qfib=fibonacciLatticePointsOnSphere(relError,1)
        points=rphitheta2xyz(qfib)    #to cartesian
        jobs=[pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
        results=np.r_[[np.asarray(job.get(0xFFFF)) for job in jobs]]
    # clean up
    pool.close()
    pool.join()
    return np.r_[results.mean(axis=0),results.std(axis=0)/np.sqrt(np.shape(results[:,0])[0])]


# noinspection PyIncorrectDocstring
def doForList(funktion, looplist, *args, **kwargs):
    """
    Calculates function for values in looplist in a pool of workers in parallel usinf multiprocessing.
    
    Like multiprocessing map_async but distributes automatically all given arguments.
    
    Parameters
    ----------
    funktion : function
        Function to process with arguments (looplist[i],args,kwargs)
        Return value of function should contain parameters or at least the loopover value to allow a check, if desired.

    looplist : list
        List of values to loop over.
    loopover : string, int,default= Not given
        Name of argument to use for looping over with values in looplist.
        If not given the first argument is used, which should be not included as argument.
    ncpu : int, optional
        | number of cpus in the pool
        | not given or 0   -> all cpus are used
        | int>0      min (ncpu, mp.cpu_count)
        | int<0      ncpu not to use
    cb : None, function
        Callback after each calculation.
    debug : int
        debug > 0 allows serial output for testing

    Returns
    -------
    list : list of function return values as  [result1,result2,.....]
           The order of return values is not explicitly synced to looplist.

    Notes
    -----
    The return array of function may be prepended with the value looplist[i] as reference.
    E.g.::

     def f(x,a,b,c,d):
         return [x,x+a+b+c+d]

    Examples
    --------
    ::

     def f(x,a,b,c,d):
        res=x+a+b+c+d
        return [x,res]
     # loop over first argument, here x
     res = js.parallel.doForList(f,looplist=range(100),a=1,b=2,c=3,d=11)
     # loop over 'd' ignoring the given d=11 (which can be omitted here)
     res = js.parallel.doForList(f,looplist=range(100),loopover='d',x=0,a=1,b=2,c=3,d=11)

    """
    output=True
    if 'output' in kwargs:
        output=False
        del kwargs['output']
    ncpu=mp.cpu_count()
    if 'ncpu' in kwargs:
        if kwargs['ncpu']<0:
            ncpu=max(ncpu+kwargs['ncpu'],1)
        elif kwargs['ncpu']>0:
            ncpu=min(ncpu,kwargs['ncpu'])
        del kwargs['ncpu']
    if 'cb' in kwargs:
        cb=kwargs['cb']
        del kwargs['cb']
    else:
        cb=None
    if 'jobGetArg' in  kwargs:
        jobGetArg=kwargs['jobGetArg']
        del kwargs['jobGetArg']
    else:
        jobGetArg=None
    if 'loopover' in kwargs:
        loopover=kwargs['loopover']
        del kwargs['loopover']
    else:
        loopover=None
    if ('debug' in kwargs and kwargs['debug']>0) or ncpu==1: # in sequence for testing purposes
        if 'debug' in kwargs.keys():
            del kwargs['debug']
        res=[]
        if output: print ('start NO pool; this is a test ')
        if isinstance(loopover,str):
            for Q in looplist:
                # noinspection PyCallingNonCallable
                res.append(funktion(*args, **dict(kwargs, **{loopover:Q})))
                if cb is not None:  cb(res[-1])
        else:
            for Q in looplist:
                # noinspection PyCallingNonCallable
                res.append(funktion(*((Q,) + args), **kwargs))
                if cb is not None:  cb(res[-1])
    else: # in parallel for production run
        if 'debug' in kwargs:del kwargs['debug']
        if output: print ('start pool of ', ncpu)
        pool = mp.Pool(ncpu)
        #we need to create a temporary dict that is given to a job and is not only a view to the updated kwargs
        # this is needed as the view changes to each new value in the loop even in the jobs
        if isinstance(loopover,str):    
            jobs=[pool.apply_async(funktion, args, dict(kwargs, **{loopover:Q}), callback=cb) for Q in looplist]
        else:
            jobs=[pool.apply_async(funktion, (Q,) + args, kwargs, callback=cb) for Q in looplist]
        res = [job.get() for job in jobs]
        # clean up
        pool.close()
        pool.join()
        if output: print ('closed pool again')
    return res


# noinspection PyIncorrectDocstring
def doForQlist(funktion, qList, *args, **kwargs):
    """
    Calculates for qlist the function in a pool of workers using multiprocessing.
    
    Calcs [function(Qi, *args, **kwargs) for Qi in qlist ] in parallel.
    The return value of function will contain the value Qi as reference.

    Parameters
    ----------
    funktion : function
        Function to process with arguments (looplist[i],args,kwargs)
    qList : list
        List of values for first argument in function.
        qList value prepends the arguments args.
    ncpu : int, optional
        | number of cpus in the pool
        | not given or 0   -> all cpus are used
        | int>0      min (ncpu, mp.cpu_count)
        | int<0      ncpu not to use
    cb :function, optional
        Callback after each calculation
    debug : int
        debug > 0 allows serial output for testing

    Returns
    -------
    list : ndim function_return.ndim+1
        The list elements will be prepended with the value qlist[i] as reference.

    Examples
    --------
    ::

     def f(x,a,b,c,d):
        return [x+a+b+c+d]
     # loop over first argument here x
     js.parallel.doForList(f,Qlist=range(100),a=1,b=2,c=3,d=11)

    """ 
    output=True
    if 'output' in kwargs:
        output=False
        del kwargs['output']

    ncpu=mp.cpu_count()
    if 'ncpu' in kwargs:
        if kwargs['ncpu']<0:
            ncpu=max(ncpu+kwargs['ncpu'],1)
        elif kwargs['ncpu']>0:
            ncpu=min(ncpu,kwargs['ncpu'])
        del kwargs['ncpu']
    if 'cb' in kwargs:
        cb=kwargs['cb']
        del kwargs['cb']
    else:
        cb=None
    if 'jobGetArg' in kwargs:
        jobGetArg=kwargs['jobGetArg']
        del kwargs['jobGetArg']
    else:
        jobGetArg=None
    if ('debug' in kwargs and kwargs['debug']>0) or ncpu==1: # in sequence for testing purposes
        res=[]
        if 'debug' in kwargs:
            del kwargs['debug']
        if output: print ('start NO pool  this is a test ')
        for Q in qList:
            # noinspection PyCallingNonCallable
            res.append(funktion(*(Q,) + args, **kwargs))
            if cb is not None:
                cb(res[-1])
    else: # in parallel for production run
        #print 'start pool of ',ncpu
        pool = mp.Pool(ncpu)
        jobs=[(Q,pool.apply_async(funktion, (Q,) + args, kwargs, callback=cb)) for Q in qList]
        res=[job[1].get(jobGetArg) for job in jobs]
        # clean up
        pool.close()
        pool.join()
        #print 'closed pool again'
    return res


