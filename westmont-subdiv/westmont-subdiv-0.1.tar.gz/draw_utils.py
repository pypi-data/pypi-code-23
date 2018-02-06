import numpy as np
import matplotlib.pyplot as plt
import matplotlib.artist as artist

class DrawUtils:
    def __init__(self, r_max=5, c=[(0,0.5), (0.5,1), (1,0.5), (0.5,0)],
    p=[1/8, 1/2, 6/8, 1/2, 1/8], k=None, subdiv=None):

        # number of iterations
        self.r_max = r_max
        self.r_current = 0

        # control points
        self.c = c
        self.c0 = c[:]

        # refinement sequence
        self.p = p

        # option for open curve rendering
        self.k = k

        # subdivision method: closed or open
        self.subdiv = subdiv

        # initialize figure, drawing
        self.fig = plt.figure(1)
        self.ax = self.fig.add_subplot(111)
        self.x_min = min(list(zip(*self.c))[0])
        self.x_max = max(list(zip(*self.c))[0])
        self.y_min = min(list(zip(*self.c))[1])
        self.y_max = max(list(zip(*self.c))[1])

        self.drawn_control_points=self.draw_c(self.c,color='r',radius=0.01*(self.x_max-self.x_min),set_gids=True,set_picker=True)
        self.on_pick_cid=self.fig.canvas.mpl_connect('pick_event', self.on_pick_event)
        self.continue_cid=self.fig.canvas.mpl_connect('button_press_event', self.continue_event)
        plt.xlim(self.x_min-.1,self.x_max+.1)
        plt.ylim(self.y_min-.1,self.y_max+.1)

        self.subdiv_results = []
        self.picked_artist = None
        self.on_press_cid = None

    def subdiv_wrapper(self):
        x = self.subdiv(x=np.array(list(zip(*self.c))[0]), p=self.p, k=self.k)
        y = self.subdiv(x=np.array(list(zip(*self.c))[1]), p=self.p, k=self.k)
        return list(zip(x,y))

    def draw_c(self, midpoints,color='r', radius=0.01, set_gids=False, set_picker=False):
        counter=0
        drawn_points = []
        for i in midpoints:
            if set_gids:
                gid=counter
            else:
                gid=None
            if type(color) is list:
                current_color = color[counter % len(color)]
            else:
                current_color = color
            circle1 = plt.Circle((i[0], i[1]), radius, color = current_color,gid=gid)
            self.ax.add_artist(circle1)
            drawn_points.append(circle1)
            circle1.set_picker(set_picker)
            counter += 1
        self.fig.canvas.draw()
        return drawn_points

    def clear_c(self, drawn_points):
        for i in drawn_points:
            i.remove()

    def on_pick_event(self,event):
        if self.picked_artist != None:
            self.picked_artist.set_color('r')
        self.picked_artist = event.artist
        event.artist.set_color('b')
        self.fig.canvas.draw()
        self.fig.canvas.mpl_disconnect(self.on_pick_cid)
        self.fig.canvas.mpl_disconnect(self.continue_cid)
        self.on_press_cid=self.fig.canvas.mpl_connect('button_press_event', self.on_press_event)

    def continue_event(self,event):
        if self.picked_artist == None and self.r_current <= self.r_max:
            self.c=self.subdiv_wrapper()
            self.clear_c(self.subdiv_results)
            self.subdiv_results=self.draw_c(self.c,color=['g','m'],radius=0.01*(self.x_max-self.x_min))

            self.r_current += 1

    def on_press_event(self,event):
        if self.picked_artist != None:
            self.continue_cid=self.fig.canvas.mpl_connect('button_press_event', self.continue_event)
            self.on_pick_cid=self.fig.canvas.mpl_connect('pick_event', self.on_pick_event)
            self.fig.canvas.mpl_disconnect(self.on_press_cid)
            new_coord=(event.xdata,event.ydata)
            j = self.picked_artist.get_gid()
            self.c0[j]=new_coord
            self.c = self.c0[:]
            self.clear_c(self.drawn_control_points)
            self.drawn_control_points=self.draw_c(self.c0,color='r',radius=0.01*(self.x_max-self.x_min),set_gids=True,set_picker=True)

            for i in range(0,self.r_current):
                self.c = self.subdiv_wrapper()
            self.clear_c(self.subdiv_results)
            self.subdiv_results=self.draw_c(self.c,color=['g','m'],radius=0.01*(self.x_max-self.x_min))

            self.picked_artist = None

    def plot_show(self):
        plt.show()
