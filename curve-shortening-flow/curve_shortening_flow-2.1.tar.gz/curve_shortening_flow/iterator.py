import numpy as np
from . import get_vertices
from . import time_step
from . import evaluation
from . import derivative
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from . import animation

class iterator:
    """
    Class for the iterator

    The iterator initializes all necessary variables and sets the initial 
    vertices.
    After the initialization a step or multiple steps can be performed.
    It will only iterate until there are only 5 or less vertices left.
    After or while doing single steps, an animation can be loaded and played.

    Flags are

    * remesh: Remeshing the curve, default is True.
    * remove: Removing vertices that are to close, default is False.
    * save: Save the vertices and some helpful variables at every step, default is True.
    * move_cm: Move the CM back to starting position, default is True.
    * cubic: Set the spline interpolation to cubic on or off. Off means linear. Default is True.
    * rescale_length: Rescale the length of the curve ons it reaches the minimal length, default is True.

    Some parameters are

    * method: Set the time stepping Method, default is "euler_forward".
    * tolerance: The tolerance for the check whether the curvature is still changing. Default is 1e-10.
    * min_length: Set the minimal length for the curve (if rescale_length is True). Default is 1/4 of the bounding box.
    """
    def __init__(self,vertices):
        """
        The initial set of vertices is once remeshed into equal distribution 
        for smoothness.

        Parameters
        ----------
        vertices: numpy array
            Numpy array of initial vertices to use. Shape needs to be (n,2).
        """
        self.vertices        = get_vertices.shift(vertices)
        self.length          = evaluation.length(self.vertices)
        self.n,_             = self.vertices.shape
        self.vertices,self.dx= time_step.remesh(self.vertices,0.,k=1)
        self.curvature       = np.sqrt(np.sum(derivative.deriva(
                                derivative.get_t(self.vertices))**2,axis=1))

        self.verticess      = {0:self.vertices}
        self.curvatures     = {0:self.curvature}
        self.iterations     = 0
        self.dt             = 0.
        self.time           = 0.
        self.mean_curv      = np.array([np.mean(self.curvature)])
        self.std_curv       = np.array([np.std(self.curvature)])
        self.times          = np.array([self.time])
        self.lengths        = np.array([self.length])
        self.cm             = evaluation.center_mass(self.vertices)
        self.cms            = np.array([self.cm])
        self.remesh         = True
        self.remove         = False
        self.save           = True
        self.move_cm        = True
        self.cubic          = True
        self.rescale_length = True
        self.min_length     = evaluation.bounding_box(self.vertices)*np.pi
        self.tolerance      = 1e-10
        self.method         = "euler_forward"

    @classmethod
    def example(cls,name="spiral"):
        """
        Initialization of the iterator with a example.

        Parameters
        ----------
        name: str, optional
            Name if the example file. Options are spiral (default), bohne, 
            some_form and ellipse

        Returns
        -------
        iterator:
            Instance of iterator class with example vertices.
        """
        vertices = get_vertices.load_example(name)
        return cls(vertices)

    def step(self):
        """
        Stepping function for a single step.

        This method only does one step and only if the number of vertices is 
        larger than 5.
        If wished it also saves the step into a dictionary and lists for 
        length and CM.
        It is possible to turn off the remeshing, which is default.
        Also the removing of points can be turned of.
        The time step method is a euler forward for now.
        """
        if self.n > 5:
            if self.remesh and not("timestep" in self.method):
                if self.cubic:
                    self.vertices,self.dx = time_step.remesh(self.vertices,
                                                            self.dt)
                else:
                    self.vertices,self.dx = time_step.remesh(self.vertices,
                                                            self.dt,k=1)

            if self.remove:
                self.vertices = time_step.remove(self.vertices,self.dx)

            if self.method == "euler_forward":
                self.vertices,self.dt   = time_step.euler_forward(
                                            self.vertices)
            elif self.method == "timestep31":
                self.vertices = time_step.timestep31(self.vertices,
                                                    1,1,1,10)
                self.dt = 1.
            elif self.method == "timestep32":
                self.vertices = time_step.timestep32(self.vertices,
                                                    1,1,10)
                self.dt = 1.
            elif self.method == "timestep33":
                self.vertices = time_step.timestep33(self.vertices,
                                                    1.,1,1,10,0.2)
                self.dt = 1.
            elif self.method == "timestep34":
                self.vertices = time_step.timestep34(self.vertices,
                                                    1.,1,1,10,0.2)
                self.dt = 1.
            
            
            if self.rescale_length and self.length < self.min_length:
                self.vertices = time_step.rescale_length(self.vertices,
                                                        self.min_length)

            if self.move_cm:
                self.vertices = time_step.cm_conservation(self.vertices,
                                                            self.cms[0])

            self.time       = self.time + self.dt
            self.length     = evaluation.length(self.vertices)
            self.cm         = evaluation.center_mass(self.vertices)
            self.n,_        = self.vertices.shape
            self.iterations = self.iterations + 1
            self.dx         = self.length/(self.n-1.)
            self.curvature  = np.sqrt(np.sum(derivative.deriva(
                                            derivative.get_t(
                                            self.vertices))**2,axis=1))
            if self.save:
                self.verticess.update({self.iterations:self.vertices})
                self.curvatures.update({self.iterations:self.curvature})
                self.times      = np.append(self.times,[self.time])
                self.lengths    = np.append(self.lengths,[self.length])
                self.cms        = np.append(self.cms,[self.cm],axis=0)
                self.mean_curv  = np.append(self.mean_curv,[np.mean(
                                                    self.curvature)],axis=0)
                self.std_curv   = np.append(self.std_curv,[np.std(
                                                    self.curvature)],axis=0)
    
    def steps(self,stps=np.inf):
        """
        Stepping function for multiple steps.

        If the vertices are supposed to be iterated over more steps, this 
        function will run until the maximum number of
        step specified are reached or until the number of vertices is lower 
        or equal to 5.

        Parameters
        -----------
        stps: int, optional
            Number of steps to perform, default is inf, which means iteration 
            until number of vertices is lower or equal 5
        """
        condition = True
        while condition:
            self.step()
            condition = condition and self.n > 5
            condition = condition and self.iterations < stps - 1
            if self.rescale_length:
                condition = condition and np.abs(self.mean_curv[-2]-
                                        self.mean_curv[-1])>self.tolerance

    def animate(self,FPS=50,name="",with_markers=False,direct_plot=False):
        """
        Animation of the vertices

        If an animation is performed this method initializes a figure and an 
        animator of the matplotlib library.
        The initial vertices are painted in blue as well as the CM.
        The last vertices are painted in green.
        The momentary vertices are painted in red and the CM in black.
        It returns the figure and axes objects in order to be displayed.

        Parameters
        -----------
        FPS: int, optional
            Number of Frames per second for the animation, default is 50.
        name: str, optional
            Name of the file without prefix. It will be saved as a MP4 file. 
            If "" then no file is saved.
        with_markers: bool, optional
            If True + markers are placed at the position of a vertex. Default 
            is False
        direct_plot: bool, optional
            If True the plot is started right away without returning figure 
            and axes objects. Default is False

        Returns
        --------
        f: figure-object
        ax: axes-object
        line_anim: animation-object
        """
        f,ax = plt.subplots()
        if with_markers:
            ax.plot(
            np.append(self.verticess[0][:,0],np.array([self.verticess[0][0,0]])
            ,axis=0),
            np.append(self.verticess[0][:,1],np.array([self.verticess[0][0,1]])
            ,axis=0),"b+-")
            ax.plot(
            np.append(self.verticess[self.iterations][:,0]
            ,np.array([self.verticess[self.iterations][0,0]]),axis=0),
            np.append(self.verticess[self.iterations][:,1]
            ,np.array([self.verticess[self.iterations][0,1]]),axis=0),"g+-")
            line, = ax.plot(
            np.append(self.verticess[0][:,0],np.array([self.verticess[0][0,0]])
            ,axis=0),
            np.append(self.verticess[0][:,1],np.array([self.verticess[0][0,1]])
            ,axis=0),"r+-")
        else:
            ax.plot(
            np.append(self.verticess[0][:,0],np.array([self.verticess[0][0,0]])
            ,axis=0),
            np.append(self.verticess[0][:,1],np.array([self.verticess[0][0,1]])
            ,axis=0),"b-")
            ax.plot(
            np.append(self.verticess[self.iterations][:,0],
            np.array([self.verticess[self.iterations][0,0]]),axis=0),
            np.append(self.verticess[self.iterations][:,1],
            np.array([self.verticess[self.iterations][0,1]]),axis=0),"g-")
            line, = ax.plot(
            np.append(self.verticess[0][:,0],np.array([self.verticess[0][0,0]])
            ,axis=0),
            np.append(self.verticess[0][:,1],np.array([self.verticess[0][0,1]])
            ,axis=0),"r-")

        if not(self.move_cm):
            ax.plot(self.cms[0,0],self.cms[0,1],'b+')
            ax.plot(
            self.cms[self.iterations,0],self.cms[self.iterations,1],'g+')
        line_cm, = plt.plot(self.cms[0,0],self.cms[0,1],'k+')

        ax.axis("equal")
        ax.axis("off")

        line_ani = anim.FuncAnimation(  f, 
                                        animation.animate.update_line, 
                                        frames=self.iterations, 
                                        interval=1./FPS*1000, 
                                        fargs=(self.verticess,line,line_cm), 
                                        blit=False)

        if name != "":
            line_ani.save("{}.mp4".format(name), fps=FPS,dpi=300)

        if direct_plot:
            plt.show()
        else:
            return f,ax,line_ani
