import numpy as np
import matplotlib.pyplot as plt
import curve_shortening_flow

class get_vertices:
    """
    Class for the HMI (Human machine interface).

    This class provides an interface for drawing curves.
    These curves can then be feed into the iterator and animated.
    The drawing can be restarted by pressing 'c' on the keyboard.
    The density of points can be adjusted by the number keys from 1 to 9.
    At 1 the maximum amount of points are drawn and at 9 the minimum.
    In order to close the drawing screen, close the figure or press 'q' or 
    'escape'.
    After closing the figure the last and dist point are also connected by a 
    line with maximum amount of points.
    Drawing is only possible without any tool picked.
    This helps drawing by zooming or panning the view.
    The number of points and the scaling factor is updated in the title.
    The functionality is:

    * Drawing by mouse movement after pressing and holding the left mouse button.
    * Setting single points by pressing and releasing the left mouse button.
    * Pressing  'b' or 'v' draws a line between the last point and the mouse pointer position.
    """
    def __init__(self,radius=3.):
        """
        Initialization with a minimal radius.

        Parameters
        ----------
        radius: double, optional
            Minimal radius to the last point to draw the new one. Default is 3.
        """
        fig, ax = plt.subplots()
        ax.axis("equal")
        ax.grid('on')
        ax.set_xlim([0.,1000.])
        ax.set_ylim([0.,1000.])
        fig.tight_layout()

        self.fig    = fig
        self.axis   = ax
        self.pres   = False
        self.radius = radius
        self.vert   = []
        self.n      = 0
        self.error  = 0
        self.fact   = 3.
        self.axis.set_title("n={}, fact=1/{}".format(self.n,np.int(self.fact)))

    def drawing(self):
        """
        Start the drawing process.
        """
        self.connect()
        plt.show()
        self.disconnect()

    def connect(self):
        """
        Connect to the button events.
        """
        self.cidpressed = self.fig.canvas.mpl_connect('button_press_event', 
                                                        self.pressed)
        self.cidrelease = self.fig.canvas.mpl_connect('button_release_event', 
                                                        self.release)
        self.cidmotion  = self.fig.canvas.mpl_connect('motion_notify_event', 
                                                        self.on_motion)
        self.cidkey     = self.fig.canvas.mpl_connect('key_press_event', 
                                                        self.key_pressed)

    def pressed(self,event):
        """
        Act on mouse button pressed.

        If no tool is selected create a vertex.
        The first vertex is a handled different because the plot has to 
        initialized.
        For every other points the same rules for setting points apply as in 
        the motion method.
        """
        if (self.fig.canvas.manager.toolbar._active is None):
            self.pres = True
            if self.n == 0:
                x,y = event.xdata,event.ydata
                self.vert.append([x,y])
                self.vert = np.array(self.vert)
                self.line, = self.axis.plot(self.vert[:,0],self.vert[:,1],
                                            'r+-')
                self.n,_ = self.vert.shape
                self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                            np.int(self.fact)))
                self.fig.canvas.draw()
            else:
                x,y = event.xdata,event.ydata
                if np.sqrt(np.sum((self.vert[-1]-[x,y])**2)) >= \
                                    self.radius*self.fact:
                    self.vert   = np.append(self.vert,np.array([[x,y]]),axis=0)
                    self.n,_    = self.vert.shape
                    self.line.set_data(self.vert[:,0],self.vert[:,1])
                    self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                            np.int(self.fact)))
                    self.fig.canvas.draw()


    def release(self,event):
        """
        Save the released state.
        """
        self.pres = False

    def on_motion(self,event):
        """
        Draw lines by moving the mouse.

        If the left mouse button is pressed and the mouse is moved, 
        vertices are drawn.
        The minimum distance of points takes is defined by the radius and its 
        scaling factor.
        Only if the next mouse position if further away then that distance a 
        new vertex is generated.
        By moving the mouse faster or slower the amounts of points takes is 
        also changed 
        but this is a problem with the figure not with the algorithm.
        If moved slow enough vertices are generated at the specified rate.
        """
        if self.pres:
            try:
                x,y = event.xdata,event.ydata
                if np.sqrt(np.sum((self.vert[-1]-[x,y])**2)) >= \
                    self.radius*self.fact:
                    self.vert   = np.append(self.vert,np.array([[x,y]]),axis=0)
                    self.n,_    = self.vert.shape
                    self.line.set_data(self.vert[:,0],self.vert[:,1])
                    self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                            np.int(self.fact)))
                    self.fig.canvas.draw()
            except:
                self.error = self.error + 1

    def interpol(self,x,y,xl,yl):
        """
        Connect two points by a line.

        This method creates a line between two points with a minimal distance 
        between points.
        The distance is controlled by the minimal radius and the scaling 
        factor.
        """
        rad = np.sqrt((x-xl)**2+(y-yl)**2)
        dx = (x-xl)/rad
        dy = (y-yl)/rad
        new_verts = np.array([[xl+i*dx,yl+i*dy] for i in np.linspace(
                                        self.radius,
                                        rad-self.radius,
                                        np.int(rad/self.radius/self.fact))])
        return  new_verts

    def key_pressed(self,event):
        """
        Key event handler.

        Options are:
        
        * 'escape' or 'q' to close the figure and connect last and first point.
        * 'b' or 'v' to connect the last point and mouse position with a line.
        * Number keys for setting the scaling of the minimal distance.
        * 'c' to clear the drawing and start from the beginning.
        """
        if event.key == "escape" or event.key == "q":
            x,y     = self.vert[0,0],self.vert[0,1]
            xl,yl   = self.vert[-1,0],self.vert[-1,1]
            self.fact = 1.
            self.vert = np.append(self.vert,self.interpol(x,y,xl,yl),axis=0)
            self.n,_    = self.vert.shape
            plt.close(self.fig)
        elif event.key == "b" or event.key == "v":
            if self.n != 0:
                x,y     = event.xdata,event.ydata
                xl,yl   = self.vert[-1,0],self.vert[-1,1]
                self.vert = np.append(self.vert,
                                    self.interpol(x,y,xl,yl),axis=0)
                self.line.set_data(self.vert[:,0],self.vert[:,1])
                self.n,_    = self.vert.shape
                self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                            np.int(self.fact)))
                self.fig.canvas.draw()
        elif event.key in ["1","2","3","4","5","6","7","8","9"]:
            self.fact = np.float(event.key)
            self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                        np.int(self.fact)))
            self.fig.canvas.draw()
        elif event.key == "c":
            try:
                self.line.remove()
            except:
                self.error = self.error + 1
            self.vert   = []
            self.n      = 0
            self.axis.set_title("n={}, fact=1/{}".format(self.n,
                                                        np.int(self.fact)))
            self.fig.canvas.draw()

    def disconnect(self):
        """
        Disconnect from the events.
        """
        self.fig.canvas.mpl_disconnect(self.cidpressed)
        self.fig.canvas.mpl_disconnect(self.cidrelease)
        self.fig.canvas.mpl_disconnect(self.cidmotion)
        self.fig.canvas.mpl_disconnect(self.cidkey)

def main():
    hmi = get_vertices()
    hmi.drawing()

    print(hmi.n)

    vit = curve_shortening_flow.iterator.iterator(hmi.vert)

    vit.steps()
    fanim,ax_anim,anim_line = vit.animate()

    plt.show()

if __name__ == "__main__":
    main()
