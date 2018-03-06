import numpy as np
import math

def get_t(daten):
    """
    Method for calculating the distance vector between vertices.

    Parameters
    ----------
    daten: numpy array
        Array of the vertices in numpy form. Shape needs to be (N,2)

    Returns
    -------
    t-vectors
        Distance vectors of the initial vertices

    """
    tvec = daten-np.roll(daten,1,axis=0)
    return np.array(tvec,dtype="float64")

def deriva(tvec,norm=True):
    """
    Method for calculating the derivative out of the distance vectors.

    Parameters
    ----------
    tvec: numpy array
        Numpy array of the t-vectors of form (N,2)
    norm: bool, optional
        If True the t-vectors are normalized

    Returns
    -------
    numpy array
        Derivative of the t-vectors in (N,2) form

    """
    if norm:
        tvec = np.array([tv/np.sqrt(np.sum(tv**2)) for tv in tvec]
                        ,dtype="float64")
    return -tvec+np.roll(tvec,-1,axis=0)

def getbeta(f,k,epsilon): #calculation of beta
    n=len(k)
    beta=[]
    for i in range(0,n):
        newbeta=epsilon*(-1)*k[i]+f
        beta.append(newbeta)
    return beta

def geth(daten): # h is the euclidean difference
    n=len(daten)
    h=[] 
    for i in range(0,n):
        if i==0:   #need this that we do not have index -1
            quad=math.pow(daten[i][0]-daten[n-1][0],2)+math.pow(daten[i][1]-daten[n-1][1],2)
        else:    
            quad=math.pow(daten[i][0]-daten[i-1][0],2)+math.pow(daten[i][1]-daten[i-1][1],2)
        h.append(math.sqrt(quad))
    return h    

def getcapitalh(daten): # differnece per component
    H=[]
    n=len(daten)
    for i in range(0,n):
        if i==0:
            dist1=daten[i][0]-daten[n-1][0]
            dist2=daten[i][1]-daten[n-1][1]
        else:
            dist1=daten[i][0]-daten[i-1][0]
            dist2=daten[i][1]-daten[i-1][1]
        dist=[dist1,dist2] 
        H.append(dist)
    return H

def getb(n,h,sigmat,f,normal,daten):  #right side of the system
    dop=2*n
    b=np.zeros(shape=(dop,1))   
    for i in range (0,n):
        if i==n-1:       #special case des index 
            b[i]=(h[0]+h[i])/(2*sigmat)*daten[i][0]
        else:            #calculation like formula
            b[i]=(h[i+1]+h[i])/(2*sigmat)*daten[i][0]
    for j in range (0,n):
        if j==n-1:
            b[j+n]=(h[0]+h[j])/(2*sigmat)*daten[j][1]
        else:
            b[j+n]=(h[j+1]+h[j])/(2*sigmat)*daten[j][1]
    return b

def getmatrix(n,alpha,epsilon,h,sigmat,daten):   #Matrix for equation
    dop=2*n
    A=np.zeros(shape=(dop,dop))
    for i in range(0,n):   #first component
        if i==0:    #1 special case
            A[i][n-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[i+1]+h[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i][i+1]=-alpha[i]/2-epsilon/h[i+1]
        elif i==n-1: #2.special case
            A[i][i-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[0]+h[i])/(2*sigmat)+epsilon/h[0]+epsilon/h[i]
            A[i][0]=-alpha[i]/2-epsilon/h[0]
        else:     #calculation
            A[i][i-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[i+1]+h[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i][i+1]=-alpha[i]/2-epsilon/h[i+1]
    for i in range(0,n):  # same for second component 
        if i==0:
            A[i+n][dop-1]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[i+1]+h[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i+n][i+n+1]=-alpha[i]/2-epsilon/h[i+1]
        elif i==n-1:
            A[i+n][i-1+n]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[0]+h[i])/(2*sigmat)+epsilon/h[0]+epsilon/h[i]
            A[i+n][n]=-alpha[i]/2-epsilon/h[0]
        else:
            A[i+n][i-1+n]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[i+1]+h[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i+n][i+n+1]=-alpha[i]/2-epsilon/h[i+1]        
    return A

def getblang(n,h,sigmat,f,normal,daten,hold,epsilon,alpha):  #version of b for 3.4
    dop=2*n
    b=np.zeros(shape=(dop,1))
    for i in range (0,n):     #more cases and longer term
        if i==0:
            b[i]=((h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)-epsilon/hold[i+1]-epsilon/hold[i])*daten[i][0]-(alpha[i]/2-epsilon/hold[i])*daten[n-1][0]+(alpha[i]/2+epsilon/hold[i+1])*daten[i+1][0]
        elif i==n-1:
            b[i]=((h[0]+h[i]+hold[0]+hold[i])/(2*sigmat)-epsilon/hold[0]-epsilon/hold[i])*daten[i][0]-(alpha[i]/2-epsilon/hold[i])*daten[i-1][0]+(alpha[i]/2+epsilon/hold[0])*daten[0][0]
        else:
            b[i]=((h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)-epsilon/hold[i+1]-epsilon/hold[i])*daten[i][0]-(alpha[i]/2-epsilon/hold[i])*daten[i-1][0]+(alpha[i]/2+epsilon/hold[i+1])*daten[i+1][0]
    for j in range (0,n):
        if j==0:
            b[n]=((h[j+1]+h[j]+hold[j+1]+hold[j])/(2*sigmat)-epsilon/hold[j+1]-epsilon/hold[j])*daten[j][1]-(alpha[j]/2-epsilon/hold[j])*daten[n-1][1]+(alpha[j]/2+epsilon/hold[j+1])*daten[j+1][1]
        elif j==n-1:
            b[j+n]=((h[0]+h[j]+hold[0]+hold[j])/(2*sigmat)-epsilon/hold[0]-epsilon/hold[j])*daten[j][1]-(alpha[j]/2-epsilon/hold[j])*daten[j-1][1]+(alpha[j]/2+epsilon/hold[0])*daten[0][1]
        else:
            b[j+n]=((h[j+1]+h[j]+hold[j+1]+hold[j])/(2*sigmat)-epsilon/hold[j+1]-epsilon/hold[j])*daten[j][1]-(alpha[j]/2-epsilon/hold[j])*daten[j-1][1]+(alpha[j]/2+epsilon/hold[j+1])*daten[j+1][1]
    return b

def getmatrixlang(n,alpha,epsilon,h,sigmat,daten,hold):  #version of Matrix for 3.4
    dop=2*n
    A=np.zeros(shape=(dop,dop))     #need one parameter more and more calculation
    for i in range(0,n):
        if i==0:
            A[i][n-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i][i+1]=-alpha[i]/2-epsilon/h[i+1]
        elif i==n-1:
            A[i][i-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[0]+h[i]+hold[0]+hold[i])/(2*sigmat)+epsilon/h[0]+epsilon/h[i]
            A[i][0]=-alpha[i]/2-epsilon/h[0]
        else:
            A[i][i-1]=alpha[i]/2-epsilon/h[i]
            A[i][i]=(h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i][i+1]=-alpha[i]/2-epsilon/h[i+1]
    for i in range(0,n):
        if i==0:
            A[i+n][dop-1]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i+n][i+n+1]=-alpha[i]/2-epsilon/h[i+1]
        elif i==n-1:
            A[i+n][i-1+n]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[0]+h[i]+hold[0]+hold[i])/(2*sigmat)+epsilon/h[0]+epsilon/h[i]
            A[i+n][n]=-alpha[i]/2-epsilon/h[0]
        else:
            A[i+n][i-1+n]=alpha[i]/2-epsilon/h[i]
            A[i+n][i+n]=(h[i+1]+h[i]+hold[i+1]+hold[i])/(2*sigmat)+epsilon/h[i+1]+epsilon/h[i]
            A[i+n][i+n+1]=-alpha[i]/2-epsilon/h[i+1]        
    return A

def getk(H,h):   #calculation of k
    n=len(H)
    k=[]
    for i in range (0,n):
        if i==0:
            det=H[n-1][0]*H[i+1][1]-H[n-1][1]*H[i+1][0]
            do=np.dot(H[n-1],H[i+1])
            cosi=do/(h[n-1]*h[i+1]) #need so plug this in to arccos
        elif i==n-1:
            det=H[i-1][0]*H[0][1]-H[i-1][1]*H[0][0]
            do=np.dot(H[i-1],H[0])
            cosi=do/(h[i-1]*h[0])
        else:    
            det=H[i-1][0]*H[i+1][1]-H[i-1][1]*H[i+1][0]
            do=np.dot(H[i-1],H[i+1])
            cosi=do/(h[i-1]*h[i+1])
        #calculation of det and dot product
        if det==0:
            sig=0
        elif det>0:
            sig=1
        else:
            sig=-1
        fac=np.arccos(cosi) # second factor
        kruem=sig/(2*h[i])*fac # whole calulation
        k.append(kruem)
    return k

def getn(daten): #n is the normal vector
    n=len(daten)
    normal=[]
    for i in range (0,n):
        if i==0:      #special cases
            erstkom=(daten[n-1][1]-daten[i+1][1])/2
            zweitkom=(daten[i+1][0]-daten[n-1][0])/2
        elif i==n-1:
            erstkom=(daten[i-1][1]-daten[0][1])/2
            zweitkom=(daten[0][0]-daten[i-1][0])/2
        else:    
            erstkom=(daten[i-1][1]-daten[i+1][1])/2
            zweitkom=(daten[i+1][0]-daten[i-1][0])/2

        tupel=[erstkom,zweitkom]
        normal.append(tupel)
    return normal

def getalpha(h,k,beta,omega):  #calculation of Alpha
    n=len(h)
    alpha=[]
    alpha.append(0)
    summedrei=0
    sumh=np.sum(h)          #sum of elements in h
    for j in range (0,n): #calculation of the sum of 3 elements
        summedrei=summedrei+beta[j]*k[j]*h[j]
    for i in range (1,n):
        alphaneu=alpha[i-1]+h[i]*beta[i]*k[i]-h[i]*summedrei/sumh+(sumh/n-h[i])*omega
        alpha.append(alphaneu)
    return alpha

def getdx(n,alpha,epsilon,h,daten):  #stepwidth
    dop=2*n
    sigmavec=[]
    for k in range(0,n):
        if k==n-1:
            num=h[0]+h[k]
            dnum=abs(epsilon/h[k]-alpha[k]/2)+abs(epsilon/h[0]-alpha[k]/2)-(epsilon/h[k]-epsilon/h[0])
        else:
            num=h[k+1]+h[k]
            dnum=abs(epsilon/h[k]-alpha[k]/2)+abs(epsilon/h[k+1]-alpha[k]/2)-(epsilon/h[k]-epsilon/h[k+1])
        if dnum>0.001:
            sig=0.5*num/dnum
        else:
            sig=1
        sigmavec.append(sig)
    if n>4:
        sigmatmax=min(sigmavec)
    else:
        sigmatmax=0.001
    return sigmatmax

def getdx2(n,alpha,epsilon,h,daten,hold): #schrittweite for 3.4
    dop=2*n
    sigmavec=[]
    for k in range(0,n):
        if k==n-1:
            num=h[0]+h[k]+hold[0]+hold[k]
            dnum=abs(epsilon/h[k]-alpha[k]/2)+abs(epsilon/h[0]-alpha[k]/2)-(epsilon/h[k]-epsilon/h[0])
        else:
            num=h[k+1]+h[k]+hold[k+1]+hold[k]
            dnum=abs(epsilon/h[k]-alpha[k]/2)+abs(epsilon/h[k+1]-alpha[k]/2)-(epsilon/h[k]-epsilon/h[k+1])
        if dnum>0.001:
            sig=0.5*num/dnum
        else:
            sig=1
        sigmavec.append(sig)
    if n>4:
        sigmatmax=min(sigmavec)
    else:
        sigmatmax=0.001
    return sigmatmax

