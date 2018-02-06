# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np

### relative imports from #####################################################
from flat import Flat
from inner_circle import InnerCircle
from notch import Notch

###############################################################################
class Wafer:
    def __init__(self, **kwargs):
        self.flats = []
        self.notches = []
        
        self.d = 156
        self.r_off = 0
        
        for key, value in kwargs.items():
            if key == 'alpha_off_deg':
                self.alpha_off_deg = value
            elif key == 'd':
                self.d = value
            elif key == 'r_off':
                self.r_off = value

        self.r = self.d / 2 # wafer radius

        ### wafer offset in polar coords.
        self.alpha_off = np.radians(self.alpha_off_deg)

        ### wafer offset in cartesian coords.
        self.x_off = self.r_off * np.cos(self.alpha_off)
        self.y_off = self.r_off * np.sin(self.alpha_off)
    
        self.offset = np.array((self.x_off, self.y_off))


    def addFlat(self, **kwargs):
        flat = Flat(self, **kwargs)
        self.flats.append(flat)

        return flat


    def addNotch(self, **kwargs):
        notch = Notch(self, **kwargs)
        self.notches.append(notch)
        
        return notch
    
        
    def addPrimaryFlat(self, **kwargs):
        self.primaryFlat = self.addFlat(**kwargs)
        self.flats.append(self.primaryFlat)
        return self.primaryFlat


    def addSecondaryFlat(self, **kwargs):
        self.secondaryFlat = self.addFlat(**kwargs)
        self.flats.append(self.secondaryFlat)
        return self.secondaryFlat

    
    def addWaferEdge(self):
        self.waferEdge = InnerCircle(
                alpha_off=self.alpha_off, r_off=self.r_off)
        
        return self.waferEdge


def all_features():
    all_flats()
    
    wafer.addNotch(
            r=r_notch, t=t_notch, alpha_notch_deg=alpha_notch_deg)


def all_flats():
    wafer.addPrimaryFlat(length=length_primary, alpha_deg=alpha_primary_deg)

    wafer.addSecondaryFlat(
        length=length_secondary,
        alpha_deg=alpha_secondary_deg)

    
def stop_sign():
    for alpha_deg in [0, 60, 120, 180, 240, 300]:
        wafer.addFlat(length=d/2, alpha_deg=alpha_deg)
    
            
###############################################################################
if __name__ == '__main__':
    d = 156. # wafer diameter

    # wafer offset in polar coords.
    alpha_off_deg = 20.
    r_off = 1.

    # primary flat
    length_primary = 32.5
    alpha_primary_deg = 0

    # secondary flat
    length_secondary = 18.
    alpha_secondary_deg = -90
    
    # notch
    r_notch = 1.12 # notch radius
    t_notch = 1.15 # notch depth
    alpha_notch_deg = 90 # notch angle

    wafer = Wafer(d=d, alpha_off_deg=alpha_off_deg, r_off=r_off)
    waferEdge = wafer.addWaferEdge()
    
    '''
    wafer.addPrimaryFlat(length=length_primary, alpha_deg=alpha_primary_deg)

    wafer.addSecondaryFlat(
        length=length_secondary,
        alpha_deg=alpha_secondary_deg)

    notch = wafer.addNotch(
            r=r_notch, t=t_notch, alpha_notch_deg=alpha_notch_deg)

    '''
    
    # all_flats()
    all_features()
    # stop_sign()
    
    plt.close('all')

    alpha_deg, y = waferEdge.contour(res_deg=1)
    plt.plot(alpha_deg, y - wafer.r, '.')
    
    for flat in wafer.flats:
    
        alpha_deg, y = flat.contour(res_deg=1)
        plt.plot(alpha_deg, y - wafer.r, '.')

    for notch in wafer.notches:        
        alpha_deg, a = notch.leftEdge.contour(res_deg=0.1)
        plt.plot(alpha_deg, a - wafer.r, '.')
    
        alpha_deg, a = notch.rightEdge.contour(res_deg=0.1)
        plt.plot(alpha_deg, a - wafer.r, '.')
            
        alpha_deg, a = notch.outerCircle.contour(res_deg=0.1)
        plt.plot(alpha_deg, a - wafer.r, '.')

    # alpha_deg, a = notch.contour()
    plt.xlim(85, 95)
    plt.ylim(-4, 2)
    plt.xlabel(r'$\alpha$ [°]')
    plt.ylabel(r'$\Delta r$ [mm]')
    
    plt.savefig(
            '..\\output\\notch_with_offset.png',
            dpi=300,
            transparent=True)