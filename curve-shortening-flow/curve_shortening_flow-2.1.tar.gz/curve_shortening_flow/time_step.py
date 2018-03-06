import numpy as np
import scipy.interpolate as sl
from . import derivative
from . import evaluation
import warnings
import math

def remesh(data,dt,k=3):
    """
    Method for remeshing.

    In this method the save distance for points to be at is evaluated and 
    then the curve remeshed.
    It is done by interpolating between all vertices with splines and use 
    this parameter curve to place vertices at equal distance.
    The only two points left out are the first end last point.
    The amount of points is adjusted according to the spacing and the time 
    step size.

    Parameters
    ----------
    data: numpy array
        Numpy array of the vertices of shape (N,2)
    dt: double
        Time step size to compare to
    k: int, optional
        Dimension for the splines. Default is 3 (cubic). Optionally would be 
        1 (linear). Only use odd values.

    Returns
    -------
    numpy array
        Numpy array of updated vertices of shape (N,2)
    double
        Space step size used in this step
    """
    n,_     = data.shape
    length  = evaluation.length(data)
    dan = np.copy(data)
    dx = length/(n-1.)
    while dx < dt*2.:
        n = n - 1
        dx = length/(n-1.)

    if remesh:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tck, u = sl.splprep(dan.T,s=0,per=n,k=k)
        snew = np.arange(0.,1.,1./(n))
        dan = np.array(sl.splev(snew,tck)).T
    return dan, dx

def remove(data,dx):
    """
    Remove vertices, that are to close together.

    Parameters
    ----------
    data: numpy array
        Numpy array of the vertices of shape (n,2).
    dx: double
        Minimal space step size for the vertices.

    Returns
    -------
    Numpy array
        Vertices with one of the ones which are to close removed.
    """
    det = derivative.get_t(data)
    dal = np.sqrt(np.sum(det**2,axis=1))
    mask = dal>dx/2.
    return data[mask,:]

def cm_conservation(data,cm_old):
    """
    Conservation of the CM

    The CM moves doe to stabilization algorithms like remeshing and removing.
    In order to counteract the vertices are shifted back by the movement of 
    the CM.
    The returned vertices have the same CM as the cm_old.

    Parameters
    ----------
    data: numpy array
        Vertices of shape (n,2).
    cm_old: numpy array
        Point where the CM of the vertices should sit. Shape is (2,).

    Returns
    -------
    numpy array
        The shifted Vertices.
    """
    cm_new  = evaluation.center_mass(data)
    shift   = cm_old - cm_new
    return data+shift

def rescale_length(data,set_length):
    """
    Rescales the length of the curve.
    
    In order to see the change in form of the curve better, the length is 
    rescaled to a specific length.
    This is done by moving every vertex outwards by the amount the length 
    has to be changed.
    This only works if the length is smaller then the final length.

    Parameters
    ----------
    data: numpy array
        Array of the vertices which are rescaled. Shape is (n,2).
    set_length: double
        Length to which the curve is rescaled.

    Returns
    -------
    numpy array
        Vertices with the rescaled length.
    """
    n,_     = data.shape
    length  = evaluation.length(data)

    direct  = derivative.deriva(derivative.get_t(data),norm=False)
    direct  = np.array([idirect/np.sqrt(np.sum(idirect**2)) 
                for idirect in direct],dtype="float64")
    shift   = direct*(length-set_length)/2./np.pi

    return data + shift

def euler_forward(data):
    """
    Simple forward Euler time step with adapted time step size.

    The stepsize is chosen such that the largest curvature is still stable.
    """
    det = derivative.get_t(data)
    der = derivative.deriva(det)
    dt = 1./np.max(np.sqrt(np.sum(der**2,axis=1)))/5.
    return data+der*dt,dt


#paper code
def timestep31(r,sigmat,epsilon,omega,f): #next time step for 3.1
    h=derivative.geth(r)
    n=len(r)
    normal=np.array(derivative.getn(r))
    H=derivative.getcapitalh(r)
    k=derivative.getk(H,h)
    beta=derivative.getbeta(f,k,epsilon)
    alpha=derivative.getalpha(h,k,beta,omega)   #calculate all values
    rneu=np.ones((n,2))
    for i in range (0,n):  #formula for next point
        if i==0:
             rneu[i]=r[i]+2*sigmat/(h[i+1]+h[i])*(epsilon*((r[i+1]-r[i])/h[i+1]-(r[i]-r[n-1])/h[i])+alpha[i]*(r[i+1]-r[n-1])/2)
        elif i==n-1:
             rneu[i]=r[i]+2*sigmat/(h[0]+h[i])*(epsilon*((r[0]-r[i])/h[0]-(r[i]-r[i-1])/h[i])+alpha[i]*(r[0]-r[i-1])/2)
        else:
            rneu[i]=r[i]+2*sigmat/(h[i+1]+h[i])*(epsilon*((r[i+1]-r[i])/h[i+1]-(r[i]-r[i-1])/h[i])+alpha[i]*(r[i+1]-r[i-1])/2)
    return rneu

def timestep32(r,epsilon,omega,f): #next timestep for 3.2
    h=derivative.geth(r)
    n=len(r)
    normal=np.array(derivative.getn(r))
    H=derivative.getcapitalh(r)
    k=derivative.getk(H,h)
    beta=derivative.getbeta(f,k,epsilon) 
    alpha=derivative.getalpha(h,k,beta,omega)   #calculate all values
    rneu=np.ones((n,2))
    sigmatm=derivative.getdx(n,alpha,epsilon,h,r)
    sigmat=sigmatm*0.9
    b=derivative.getb(n,h,sigmat,f,normal,r)
    A=derivative.getmatrix(n,alpha,epsilon,h,sigmat,r)
    x = np.linalg.solve(A, b)   #solve the equation
    m=len(x)
    for i in range(0,n):   #write it into 2-dim Array
        rneu[i,0]=x[i]
    for j in range(0,n):
        rneu[j,1]=x[j+n]
    return rneu    


def timestep33(r,sigmat,epsilon,omega,f,tol): #next timestep for  3.3
    boolean=0
    hold=derivative.geth(r)
    while boolean==0:        #loop until we arrive at tol
        h=derivative.geth(r)
        lenold=sum(h) 
        n=len(r)
        normal=np.array(derivative.getn(r))
        H=derivative.getcapitalh(r)
        k=derivative.getk(H,h)
        beta=derivative.getbeta(f,k,epsilon)
        alpha=derivative.getalpha(h,k,beta,omega) #calculate all values
        sigmatnorm=sigmat
        schritt=derivative.getdx(n,alpha,epsilon,h,r)  
        if sigmat>schritt:
            sigmat=schritt*0.9       #stepwidth if old one is too large
        rneu=np.ones((n,2))
        b=derivative.getb(n,h,sigmat,f,normal,r)
        A=derivative.getmatrix(n,alpha,epsilon,h,sigmat,r)
        x = np.linalg.solve(A, b)      #solve equation
        m=len(x)
        for i in range(0,n):      #write into  2-dim array
            rneu[i,0]=x[i]
        for j in range(0,n):
            rneu[j,1]=x[j+n]
        h=derivative.geth(rneu)
        lennew=sum(h)        
        dif=abs(lenold-lennew) 
        sigmat=sigmatnorm
        r=np.copy(rneu)
        if(dif<tol):        #testing the condition to end loop
            boolean=1
    return rneu 


def timestep34(r,sigmat,epsilon,omega,f,tol): #next time step 3.4
    boolean=0
    hold=derivative.geth(r)
    h=derivative.geth(r)
    counter=1
    normal=np.array(derivative.getn(r))
    H=derivative.getcapitalh(r)
    k=derivative.getk(H,h)
    beta=derivative.getbeta(f,k,epsilon)
    alphaold=derivative.getalpha(h,k,beta,omega)
    while boolean==0:# loop until tol
        counter=counter+1
        h=derivative.geth(r)
        lenold=sum(h) 
        n=len(r)
        normal=np.array(derivative.getn(r))
        H=derivative.getcapitalh(r)
        k=derivative.getk(H,h)
        beta=derivative.getbeta(f,k,epsilon)
        alpha=derivative.getalpha(h,k,beta,omega) #calculation of values
        sigmatnorm=sigmat
        schritt=derivative.getdx2(n,alpha,epsilon,h,r,hold)  
        if sigmat>schritt:
            sigmat=schritt*0.9       #stepwidth if old is too big
        rneu=np.ones((n,2))
        b=derivative.getblang(n,h,sigmat,f,normal,r,hold,epsilon,alphaold)
        A=derivative.getmatrixlang(n,alpha,epsilon,h,sigmat,r,hold)
        x = np.linalg.solve(A, b)      #solve equation
        m=len(x)
        for i in range(0,n):      #write into 2-dim array
            rneu[i,0]=x[i]
        for j in range(0,n):
            rneu[j,1]=x[j+n]
        h=derivative.geth(rneu)
        lennew=sum(h)        
        dif=abs(lenold-lennew) 
        sigmat=sigmatnorm
        r=np.copy(rneu)
        if(dif<tol):        #testing the condition to end loop
            boolean=1       
    return rneu 

