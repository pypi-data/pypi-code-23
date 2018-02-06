# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt

### imports from ##############################################################
from matplotlib import collections

###############################################################################
class WaferEdgeProfileTemplate:
    def __init__(self, thickness):
        self.t = thickness

        Ax = 76
        Bx = 508

        Cy = 2 * self.t / 3
        Cy_lower = self.t / 3

        Dy = 76

        self.A = (Ax, self.t)
        self.B_upper = (Bx, self.t)
        self.B_lower = (Bx, 0)
        self.C_upper = (51, Cy)
        self.C_lower = (51, Cy_lower)
        self.D = (0, self.t - Dy)
        self.O = (0, self.t)

        self.upperTemplate = self.O, self.D, self.A
        self.lowerTemplate = (0, 0), (Ax, 0), (0, Dy)

        self.innerTemplate = (
                self.C_upper, self.C_lower, self.B_lower, self.B_upper
        )

        self.patches = {}
        self.initPatches()

    def initPatches(self):
        p = collections.PolyCollection((self.upperTemplate,))
        self.patches['upper template'] = p
               
        p = collections.PolyCollection((self.lowerTemplate,))
        self.patches['lower template'] = p

        p = collections.PolyCollection((self.innerTemplate,))
        self.patches['inner template'] = p

        
    def plot(self):

        ### plot SEMI wafer edge profile template
        
        ax = plt.axes()
        
        for key, p in self.patches.items():
            ax.add_collection(p)

        title = "$t$ = " + str(int(self.t)) + " $\mu$m"
        plt.title(title)

###############################################################################
def main():
    waferThickness = 650

    t = WaferEdgeProfileTemplate(waferThickness)

    ### plot SEMI wafer edge profile template
    plt.close('all')
    plt.figure(1, figsize=(5,5))

    t.plot()

    plt.axes().set_aspect('equal')
    plt.xlim(-50, 700)
    plt.ylim(-50, 700)

    pngFile = '..\\output\\SEMI_wafer_edge_profile_template.png'
    plt.savefig(pngFile, dpi = 300, transparent = True, bbox_inches='tight')


###############################################################################
if __name__ == '__main__':
    main()