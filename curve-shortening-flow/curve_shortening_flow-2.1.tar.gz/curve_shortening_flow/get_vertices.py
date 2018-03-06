import numpy as np
import matplotlib.pyplot as plt
import math
import scipy.misc as sm
import time
import os

def make_ellipse(n=10,a=40.,b=20.,tilt=-np.pi/6.):
    """
    Create the vertices for a ellipse or circle.

    If a mathematical correct ellipse or circle is necessary, this method will 
    create the vertices.
    It generates a ellipse with two radii, a and b.
    If a and b are equal a circle is generated.
    It is also possible to tilt the ellipse by some portion of pi.

    Parameters
    ----------
    n: int, optional
        Number of vertices.
    a: double, optional
        First radius of the ellipse.
    b: double, optional
        Second radius of the ellipse.

    Returns
    -------
    Numpy array
    """
    dphi = np.linspace(0,2*np.pi-1./n,n)
    ci = np.array([[a*np.cos(theta+tilt),b*np.sin(theta-tilt)]
                for theta in dphi])
    return np.array(ci)

def make_rectangle(n=200,a=400,b=40):
    """
    Generate a rectangle curve.

    The rectangle is generated with two side lengths a and b.
    If both are the same a square is produced.

    Parameters
    ----------
    n: int, optional
        Number of points used in the rectangle
    a: int, optional
        First side length in pixel.
    b: int, optional
        Second side length in pixel.

    Returns
    -------
    numpy array:
        Vertices of shape (n,2)
    """
    x0,y0   = 0.,0.
    n4      = np.int(n/4.)
    dx      = 1./n
    vert    = np.array([[x0+i,y0] for i in np.linspace(dx,a,n4)])
    x0      = x0 + a
    vert    = np.append(vert,[[x0,y0+i] for i in np.linspace(dx,b,n4)],axis=0)
    y0      = y0 + b
    vert    = np.append(vert,[[x0-i,y0] for i in np.linspace(dx,a,n4)],axis=0)
    x0      = x0 - a
    vert    = np.append(vert,[[x0,y0-i] for i in np.linspace(dx,b,n4)],axis=0)
    return vert

def shift(vert):
    """
    Shift the center of mass to (0,0)
    """
    n,_ = vert.shape
    if n > 0:
        xmin = np.min(vert[:,0])
        xmax = np.max(vert[:,0])
        ymin = np.min(vert[:,1])
        ymax = np.max(vert[:,1])
        shift = [(xmax+xmin)/2.,(ymax+ymin)/2.]
        for i in range(n):
            vert[i] = vert[i] - shift
    return vert

def load_example(name="rectangle"):
    """
    Load an example file or generate example with CM (0,0).

    Options for name are:

    * spiral
    * bohne
    * some_form
    * ellipse
    * circle
    * square
    * rectangle

    Raises
    ------
    Name Error
        If name is not a example.
    """
    vertices = []
    path = os.path.join(os.path.dirname(__file__),'examples')
    if name=="spiral":
        vertices = np.load(os.path.join(path,"spiral.npy"))
    elif name=="bohne":
        vertices = np.load(os.path.join(path,"bohne.npy"))
    elif name=="some_form":
        vertices = np.load(os.path.join(path,"some_form.npy"))
    elif name=="circle":
        vertices = make_ellipse(n=100,a=40.,b=40.,tilt=0)
    elif name=="ellipse":
        vertices = make_ellipse(n=100)
    elif name=="square":
        vertices = make_rectangle(a=40,b=40)
    elif name=="rectangle":
        vertices = make_rectangle()
    else:
        raise NameError("No example found for {}".format(name))

    return shift(vertices)

def get_next_vertex(data):
    """
    Check where the next vertex sits on the curve and return it.

    It does not care how many vertices are on the edge of the square it checks,
    it returns all of theme.

    Parameters
    -----------
    data: numpy array
        Data array with the part of the curve, that is being evaluated

    Returns
    -------
    touple
        Coordinates of the next vertex
    """
    k,l = data.shape
    point = []
    left    = data[0,:]
    if np.max(left) != 0.:
        point.append([0,np.argmax(left)])
    upper   = data[:,l-1]
    if np.max(upper) != 0.:
        point.append([np.argmax(upper),l-1])
    right   = data[k-1,:]
    if np.max(right) != 0.:
        point.append([k-1,np.argmax(right)])
    lower   = data[:,0]
    if np.max(lower) != 0.:
        point.append([np.argmax(lower),0])
    point = np.array(point)
    x,y = point.shape
    if x!=2 or y!=2:
        if point[0,0] == point[1,0] and point[0,1] == point[1,1]:
            return point[1:]
        else:
            return point
    else:
        return point

def get_vertices(data,N):
    """
    Generate a list of vertices from an image.

    The input data is an numpy array of equal dimensions (n,n) and a distance 
    between the vertices.
    The data is scanned for a pixel that is at max value, which is the starting 
    point.
    Afterwards a square is put around that point with the dimensions specified 
    by N.
    The functions get_next_vertex is called and produces the next vertices.
    The one with the larges distance to the last one is used for the next 
    iteration and added to the others.
    If the last vertex sits close to the first vertex the iteration if over.
    A maximum of 10000 vertices is generated, because the curve might loop on 
    its own and become longer than it should.#
    
    Parameters
    ----------
    data: numpy array
        Array with shape (n,n) of the image to be sampled. The curve should 
        be at max value, while the rest is at min value.

    N: int
        Max distance in pixels that is sampled.

    Returns
    -------
    array
        Numpy array with all the vertices generated of shape (m,2).
    """
    k,l = data.shape
    u = np.zeros((1,2),dtype="int32")
    weiter = True
    for i in range(k):
        for j in range(l):
            if data[i,j] != 0. and weiter:
                u[0,:] = [i,j]
                weiter = False
    #print u[0,:]

    last_point = u[0,:]
    i = 0
    while (np.sqrt((u[i,0]-u[0,0])**2+(u[i,1]-u[0,1])**2) > N or i < 3) \
            and (i<10000):
        temp = data[u[i,0]-N:u[i,0]+N,u[i,1]-N:u[i,1]+N]
        poin = get_next_vertex(temp)

        fst_poin = np.copy(poin[0])
        snd_poin = np.copy(poin[1])

        fst_poin = u[i]+fst_poin-N*np.ones(2,dtype='int32')
        snd_poin = u[i]+snd_poin-N*np.ones(2,dtype='int32')

        fst_r = np.sqrt(np.sum((fst_poin-last_point)**2))
        snd_r = np.sqrt(np.sum((snd_poin-last_point)**2))
        #print fst_r,snd_r

        if fst_r >= snd_r:
            u = np.append(u,[fst_poin],axis=0)
        else:
            u = np.append(u,[snd_poin],axis=0)

        last_point = u[i]
        #print i,fst_poin,snd_poin,u[i+1,:]
        i = i+1

    return u

def main():
    name = "spiral.png"
    #data = make_circle(n=1000)
    data = np.invert(sm.imread(name,mode='L'))
    k,l = data.shape
    #data = np.pad(data,500-k,'constant')
    vl = []
    vx = []

    #"""
    dist = []
    for n in reversed(range(2,20)):
        start = time.time()
        vertices = get_vertices(data,n)
        vl.append(laenge(vertices))
        dist.append(n)
        k,l = vertices.shape
        vx.append(k)
        #print n,"{}s".format(time.time()-start)
    #"""
    vertices = get_vertices(data,18)
    np.save(name[:-3]+"npy",vertices)

    #print vertices
    k,l = vertices.shape
    #print k,l

    f, ax1 = plt.subplots()
    ax1.imshow(data,cmap='gray_r',origin='lower')
    data_t = np.ones_like(data)*0.
    for k in range(k):
        data_t[np.int(vertices[k,0]),np.int(vertices[k,1])] = 1.
    ax1.imshow(data_t,cmap='gray_r',alpha=0.7,origin='lower')
    ax1.grid('on')
    f = plt.figure()
    plt.plot(vertices[:,1],vertices[:,0])
    plt.axis("equal")
    f = plt.figure()
    plt.plot(dist,vl)
    plt.show()


if __name__ == "__main__":
    main()
