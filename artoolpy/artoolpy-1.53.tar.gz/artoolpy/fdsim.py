'''
Contains a wrapper for frequency domain simulation using ARTool
'''
from __future__ import print_function
import uuid
import numpy as np
from artsimdefs import ARTRootObject, ARTCreateSimulator, \
    ARTSetFrequencyRange, ARTRootDestroy, \
    ARTCreateCircuit, ARTCreateElement, \
    ARTAppendReference, ARTSetParameter, \
    ARTGetLength, ARTGetValue, ARTGetTriple, \
    ARTInputImpedance, ARTInputImpedanceElem


DOMAIN = 'FrequencyDomain'.encode()
WAVE_PROP_PLANE = 'PlaneWave'.encode()
CONE = 'Cone'.encode()
CYLINDER = 'Cylinder'.encode()


class FDsim:
    '''
    Attempt to make frequency domain simulations
    using ARTool easier.
    '''

    def __init__(self, borelist, slice_width=0,
                 scale_z=1, scale_r=1, use_cones=False, sim_name=None):
        self.root = ARTRootObject()
        if not sim_name:
            # assigning a unique name to simulation
            sim_name = uuid.uuid4().hex

        self.sim = ARTCreateSimulator(sim_name.encode(),
                                      DOMAIN,
                                      WAVE_PROP_PLANE)
        self.set_ins(borelist=borelist,
                     slice_width=slice_width,
                     scale_z=scale_z, scale_r=scale_r,
                     use_cones=use_cones)
        self.zin_profiles = {}
        self.set_freq_range()
        return

    def __del__(self):
        ARTRootDestroy()
        print('ARTRoot destroyed')
        return

    def set_freq_range(self, fmin=10, fmax=2000, fstep=10):
        '''
        sets the frequency range for the ARTool simulation
        '''
        ARTSetFrequencyRange(self.sim, fmin, fmax, fstep)
        self.imp = []
        return

    def set_ins(self, borelist, slice_width,
                scale_z, scale_r, use_cones):
        '''
        Creates an instrument (circuit) in artool
        using the given borelist
        NOTE: ARTool expects measurements in cms.
        borelist: (CSV - r, z)
        slice_width: the length of each slice (in cm)
        scale_z: scaling factor for z (100 if borelist is in m)
        scale_r: scaling factor for r (200 if borelist contains diameter in m)
        use_cones: creates an instrument with cone element instead of cylinders
        '''
        (r, z) = self.__read_borelist(borelist,
                                      scale_z=scale_z, scale_r=scale_r,
                                      slice_width=slice_width)

        self.ins = ARTCreateCircuit(self.sim,
                                    borelist.split('.')[0].encode())
        self.imp = []
        self.elements = []
        elem_name = 'Cyl_0'.encode()
        self.elements.append(ARTCreateElement(self.sim, elem_name, CYLINDER))
        ARTSetParameter(self.sim, '{e}.r = {r}; {e}.length = {w};'.format(
            e=elem_name, r=r[0], w=z[0]).encode())
        ARTAppendReference(self.ins, self.elements[0])

        if use_cones:
            self.__create_con_ins(r, z)
        else:
            self.__create_cyl_ins(r, z)
        return

    def __read_borelist(self,
                        borelist,
                        slice_width=0,
                        scale_z=1,
                        scale_r=1):
        '''
        reads x y values from file and adds rim
        scale_z=1000 (when the values are in mm)
        scale_r=2000 (when the values are diameter and in mm)
        '''
        # get x, y coordinates from file
        with open(borelist, 'r') as f:
            try:
                z, r = np.loadtxt(f,
                                  usecols=(0, 1),
                                  delimiter=',',
                                  unpack=True)
            except IndexError:  # does this work?
                z, r = np.loadtxt(f,
                                  usecols=(0, 1),
                                  unpack=True)
            z = z/scale_z
            r = r/scale_r

        if slice_width:
            z_sliced = np.arange(slice_width, z[-1]+slice_width, slice_width)
            r_sliced = np.interp(z_sliced, z, r)
        else:
            z_sliced = z
            r_sliced = r

        return (r_sliced, z_sliced)

    def __create_cyl_ins(self, r, z):
        '''
        Creates an instrument for the give (r,z) as a series of cones
        TODO: add bore jump elements
        '''
        for i in range(1, len(r)):
            elem_name = 'Cyl_' + str(z[i])
            self.elements.append(ARTCreateElement(self.sim,
                                                  elem_name.encode(),
                                                  CYLINDER.encode()))
            parameter = '{e}.r = {r}; {e}.length = {w};'.format(
                e=elem_name,
                r=r[i-1],
                w=z[i]-z[i-1]).encode()
            ARTSetParameter(self.sim, parameter)
            ARTAppendReference(self.ins, self.elements[-1])

        return

    def __create_con_ins(self, r, z):
        '''
        Creates an instrument for the give (r,z) as a series of cones
        TODO: add bore jump elements
        '''
        for i in range(1, len(r)):
            elem_name = 'Con_' + str(z[i])
            self.elements.append(ARTCreateElement(self.sim, elem_name.encode(),
                                                  CONE))
            parameter = '{e}.r1={r1}; {e}.r2={r2}; {e}.length={w};'.format(
                e=elem_name,
                r1=r[i-1],
                r2=r[i],
                w=z[i]-z[i-1]).encode()
            ARTSetParameter(self.sim, parameter)
            ARTAppendReference(self.ins, self.elements[-1])

        return

    def save_zin(self):
        '''
        calculates input impedance of the instrument and
        saves it in the imp property
        '''
        zin = ARTInputImpedance(self.ins)
        self.imp = self.__get_imp_values(zin)
        return

    def save_zin_profile(self, freq):
        '''
        gets the input impedance profile along the instrument
        for a given frequency (in Hz)
        '''
        if not self.imp:
            self.save_zin()

        try:
            idx = self.imp['f'].tolist().index(freq)
        except ValueError:
            idx = min(range(len(self.imp['f'])),
                      key=lambda i: abs(self.imp['f'][i]-freq))
            print('{fin} missing, returning {f}'.format(fin=freq,
                                                        f=self.imp['f'][idx]))

        self.zin_profiles[freq] = []
        for element in self.elements:
            zin = ARTInputImpedanceElem(element)
            zin_elem = self.__get_imp_values(zin)
            self.zin_profiles[freq].append(zin_elem['mag'][idx])
        return

    def __get_imp_values(self, imp_pointer):
        '''
        returns a dict of impedance values
        '''
        imp = ARTGetValue(imp_pointer)
        n = ARTGetLength(imp)
        imp_val = {'f': np.empty(n),
                   're': np.empty(n),
                   'im': np.empty(n),
                   'mag': np.empty(n)}  # clearing past values
        for i in range(n):
            tri = ARTGetTriple(imp, i)
            imp_val['f'][i] = tri.f
            imp_val['re'][i] = tri.re
            imp_val['im'][i] = tri.im
            imp_val['mag'][i] = np.sqrt(tri.re**2 + tri.im**2)

        return imp_val
