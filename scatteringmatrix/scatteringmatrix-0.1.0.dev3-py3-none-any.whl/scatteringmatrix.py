"""This module implements a 1D optical scattering matrix algorithm

This module is focused around an implementation of a 1D scattering
matrix algorithm for the purpose of calculating the optical reflection,
transmission, and absorption of multilayer stacks. In addition, there
are a variety of optical/photonic functions meant to assist in the use
of this module. This module is further divided into four sections: Units,
Photonic Functions, Multilayer Structures, and Scattering Matrix Calculations.

Imported Modules: math, csv, numpy, scipy

Units
-----
Classes:
    Units - A series of useful constants and conversion multipliers
    
Photonic Functions
------------------
Functions:
    ev_to_wavelength - convert from eV to wavelenghth in m
    transmission_angle - get the angle of transmission for optical interface
    get_kz - get the k-value in the direction of propogation
    reflection_TE - calculate the TE-mode complex reflection at an 
                    optical interface
    transmission_TE - calculate the TE-mode complex transmission at an 
                    optical interface
    reflection_TM - calculate the TM-mode complex reflection at an 
                    optical interface
    transmission_TM - calculate the TM-mode complex transmission at an 
                    optical interface
    blackbody_spectrum - Emitted power from a blackbody at specific wavelength 
                         and temperature
    create_spectrum_from_csv - Creates a funtion that returns the power at a 
                              wavelength based on a csv
                         
    
Multilayer Structures
---------------------
Classes:    
    SingleLayer - A single index layer in a multilayer stack
    LayerList - A list of layers (a stack)

Functions:
    create_multilayer - Create a layer list made up of repeating layers
    single_index_function - generate a function that returns a constant index
    generate_mixed_medium_approximation - Creates a function that returns the 
                                          mixed medium approximated index
    generate_index_from_csv - generate a function that returns an index based
                              on csv file data
    generate_index_from_SOPRA_nk - generate a function that returns an index 
                                   based on SOPRA nk file data
    create_graded_mixed_index - Creates a multilayer that has a varying mixed 
                                medium index
    

Scattering Matrix Calculations
------------------------------
Functions:
    scattering_matrix_calculation - return the transmission, reflection, and
                                    absorption for a given layer list   
    
"""
import math
import csv
import numpy as np
import scipy as sp
from scipy import interpolate

"""
------------
DEFINE UNITS
------------
"""
class Units:
    """Constants and units useful for optical calculations"""
    #Distance Units
    METERS = 1.0
    CENTIMETERS = 10.0**-2
    MILLIMETERS = 10.0**-3
    MICROMETERS = 10.0**-6
    NANOMETERS = 10.0**-9
    
    #Frequency Units
    HERTZ = 1.0
    KILOHERTZ = 10.0**3
    MEGAHERTZ = 10.0**6
    GIGAHERTZ = 10.0**9
    
    #Time Units
    SECONDS = 1.0
    MILLISECONDS = 10.0**-3
    MICROSECONDS = 10.0**-6
    NANOSECONDS = 10.0**-9
    PICOSECONDS = 10.0**-12
    FEMTOSECONDS = 10.0**-15
    
    #Physical Constants
    C_0 = 3.0*10**8 #speed of light in a vacuum
    MU_0 = 4.0*math.pi*10**-7 #vacuum permeability
    EPSILON_0 = 8.85418*10**-12 #vacuum permittivity
    H = 6.62607004*10**-34 #Planck's Constant
    EV = 1.60218*10**-19 #Electron charge
    K = 1.38064852*10**-23 #Boltzmann constant

"""
------------------------
BASIC PHOTONIC FUNCTIONS
------------------------
"""
def eV_to_wavelength(eV):
    """Converts photon energy in electron volts to wavelength in m
    
    Arg:
        eV(float): energy in electron volts

    Returns:
        float: wavelength in m    
    """
    return (Units.H*Units.C_0)/(eV*Units.EV)

def transmission_angle(index1, index2, incident_angle):
    """The complex transmitted angle from an initial angle using Snell's law
    
    Arg:
        index1(complex): index of refraction for the first medium
        index2(complex): index of refraction for the second medium
        incident_angle(complex): angle of incidence (in first medium)

    Returns:
        complex: propogation angle in second medium
    
    Note: numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
    """
    return np.arcsin((index1/index2)*np.sin(incident_angle))

def get_kz(index, angle, wavelengths):
    """The wavenumber component in the z-direction (corresponding to 0 degrees)
    
    Arg:
        index(complex): index of refraction for the first medium
        angle(complex): angle of propagagtion
        wavelength(float): vacuum wavelength

    Returns:
        complex: wavenumber in z direction in second medium
    
    Note: numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
    """
    return (2.0*np.pi*index*np.cos(angle))/wavelengths
	
def reflection_TE(index1, index2, incident_angle):
    """The complex reflection of a TE wave at an interface
    
    Arg:
        index1(complex): index of refraction for the first medium
        index2(complex): index of refraction for the second medium
        incident_angle(complex): angle of incidence (in first medium)

    Returns:
        complex: reflection magnitude and phase relative to incident wave
    
    Notes: 
        - numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
        - Fresnel equations used
    """
    transmitted_angle = transmission_angle(index1, index2, incident_angle)
    part1 = index1*np.cos(incident_angle)
    part2 = index2*np.cos(transmitted_angle)
    return (part1-part2)/(part1+part2)

def transmission_TE(index1, index2, incident_angle):
    """The complex transmission of a TE wave at an interface
    
    Arg:
        index1(complex): index of refraction for the first medium
        index2(complex): index of refraction for the second medium
        incident_angle(complex): angle of incidence (in first medium)

    Returns:
        complex: transmission magnitude and phase relative to incident wave
    
    Notes: 
        - numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
        - Fresnel equations used
    """
    transmitted_angle = transmission_angle(index1, index2, incident_angle)
    part1 = index1*np.cos(incident_angle)
    part2 = index2*np.cos(transmitted_angle)
    return (2.0*part1)/(part1+part2)

def reflection_TM(index1, index2, incident_angle):
    """The complex reflection of a TM wave at an interface
    
    Arg:
        index1(complex): index of refraction for the first medium
        index2(complex): index of refraction for the second medium
        incident_angle(complex): angle of incidence (in first medium)

    Returns:
        complex: reflection magnitude and phase relative to incident wave
    
    Notes: 
        - numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
        - Fresnel equations used
    """
    transmitted_angle = transmission_angle(index1, index2, incident_angle)
    part1 = index2*np.cos(incident_angle)
    part2 = index1*np.cos(transmitted_angle)
    return (part1-part2)/(part1+part2)

def transmission_TM(index1, index2, incident_angle):
    """The complex transmission of a TM wave at an interface
    
    Arg:
        index1(complex): index of refraction for the first medium
        index2(complex): index of refraction for the second medium
        incident_angle(complex): angle of incidence (in first medium)

    Returns:
        complex: transmission magnitude and phase relative to incident wave
    
    Notes: 
        - numpy arrays of complex numbers of equal dimension can also be used, 
          with the return value being an array of complex numbers of equal
          dimension
        - Fresnel equations used
    """
    transmitted_angle = transmission_angle(index1, index2, incident_angle)
    part1 = index2*np.cos(incident_angle)
    part2 = index1*np.cos(transmitted_angle)
    return (2.0*(index1/index2)*part1)/(part1+part2)

def blackbody_spectrum(temperature, wavelength):
    """Emitted power from a blackbody at specific wavelength and temperature
    
    Arg:
        temperature(float): the blackbody temperature in kelvin
        wavelength(float): the wavelength in meters
        
    Returns:
        float: emitted power in watts per meter squared per meter
    
    Notes: 
        - the wavelength can be a numpy array of real numbers, with the return 
          value being an array of of equal dimension
    """
    part1 = (2.0*Units.H*Units.C_0**2)/(wavelength**5)
    part2 = 1.0/(np.exp(Units.H*Units.C_0/(wavelength*Units.K*temperature))-1.0)
    return part1*part2
    
def create_spectrum_from_csv(filename, type_str="nm_W"):
    """Creates a funtion that returns the power at a wavelength based on a csv
    
    Arg:
        filename(string): The csv file to be used
        type(string): the type of file to be opened. This can be either:
                        - "nm_W": stored as nm,Watts with headings
        
    Returns:
        callable: returns the power at a given wavelength (per unit wavelength) 
                  given the data in the csv
    """
    if(type_str=="nm_W"):
        nm_list, power_list = list(), list()
        with open(filename) as csv_file:
            reader = csv.reader(csv_file, skipinitialspace = True)             
            next(reader)
            for row in reader:
                nm_list.append(float(row[0]))
                power_list.append(float(row[1]))
        wavelengths = sp.array(nm_list)*Units.NANOMETERS
        power = sp.array(power_list)
        get_power = interpolate.interp1d(wavelengths, power, bounds_error=False,
                                         fill_value=(power[0],power[-1]))
        return lambda x: 1.0*get_power(x)
    
"""
---------------------
MULTILAYER STRUCTURES
---------------------
"""

class SingleLayer:
    """This is a single layer of a 1D multilayer structure

    Attributes:
        thickness(float): the thickness of the layer in meters
        get_index(callable): a function that returns a complex index of
                             refraction for a specific wavelength. The
                             function must be of the form...
                             f(float): return complex
    """
    def __init__(self, index_function, thicknessInit = 0):
        self.thickness = thicknessInit
        self.get_index = index_function

class LayerList(list):
    """This is a list of SingleLayers"""
    def __init__(self):        
        list.__init__(self)

def create_multilayer(index_func_list, thickness_list):
    """Create a layer list made up of repeating layers
    
    The function cycles through the index and thickness lists, adding 
    SingleLayers to a LayerList until all the thickness_list is complete.
    
    Arg:
        index_func_list(iterable of callables): this is a list or array or
                                                similar iterable of index
                                                functions to be repeated
                                                in the multilayer
        thickness_list(iterable of floats): this is the list of the thickness
                                            of every layer
        
    Returns:
        LayerList: resulting multilayer from the two lists
    """
    multilayer = LayerList()
    numLayerTypes = len(index_func_list)
    numLayers = len(thickness_list)
    for i in range(numLayers):
        type_index = i % numLayerTypes
        multilayer.append(SingleLayer(index_func_list[type_index], 
                                      thickness_list[i]))
    return multilayer
        
def single_index_function(index):
    """Creates a function that returns an index for every single wavelength
            
    Arg:
        index(complex): the index of refraction to be returned
        
    Returns:
        callable: returns the complex index for an argument of any float 
    """
    get_index = lambda wavelengths: index
    return get_index

def generate_mixed_medium_approximation(fraction_1, index_func_1, index_func_2,
                                        mix_type = "bruggeman"):
    """Creates a function that returns the mixed medium approximated index
    
    Arg:
        fraction_1(float): The volume fraction of index 1
        index_func_1(callable): the index returning function of medium 1
        index_func_2(callable): the index returning function of medium 2
        mix_type (string): the type of approximation formula used
                            - bruggeman: Bruggeman approximation used
                            - MG: Maxwell-Garnett apporximation used
        
    Returns:
        callable: returns the complex index given the mixture of those two
                  media
    """
    
    if(mix_type == "MG"):
        def porous_index(wavelength):
            epsilon_1 = index_func_1(wavelength)**2.0
            epsilon_2 = index_func_2(wavelength)**2.0
            numer = 3*epsilon_2-2*fraction_1*epsilon_2+2*fraction_1*epsilon_1
            denom = 3*epsilon_1+fraction_1*epsilon_2-fraction_1*epsilon_1
            new_epsilon = (numer/denom)*epsilon_1
            new_index = np.sqrt(new_epsilon)
            return new_index
        return porous_index    
    
    else:
        def porous_index(wavelength):
            a = -2.0
            b = ((3.0*fraction_1-1.0)*index_func_1(wavelength)
                +(2.0-3.0*fraction_1)*index_func_2(wavelength))
            c = index_func_1(wavelength)*index_func_2(wavelength)
            new_index = (-b-np.sqrt(b**2-4*a*c))/(2.0*a)
            return new_index
        return porous_index

def generate_index_from_csv(filename, type_str="eV_Epsilon", delimiter=",", 
                            skip_first_line = True):
    """Creates a function that returns the index based on a csv file
    
    Arg:
        filename(string): The csv file to be used
        type(string): the type of file to be opened. This can be either:
                        - "eV_Epsilon": stored as eV,er,ei with headings
                        - "um_nk": stored as um,n,k, with headings
        
    Returns:
        callable: returns the complex index given the data in the csv
    """
    if(type_str=="eV_Epsilon"):
        eV_list, er_list, ei_list = list(), list(), list()
        with open(filename) as csv_file:
            reader = csv.reader(csv_file, delimiter = delimiter, 
                                skipinitialspace = True)             
            if(skip_first_line):
                next(reader)
            for row in reader:
                eV_list.append(float(row[0]))
                er_list.append(float(row[1]))
                ei_list.append(float(row[2]))
        eV = sp.array(eV_list)
        wavelengths = eV_to_wavelength(eV)
        epsilon = sp.array(er_list) + 1.0j*sp.array(ei_list)
        index = np.conj(np.sqrt(epsilon))
        get_index = interpolate.interp1d(wavelengths, index, bounds_error=False,
                                         fill_value=(index[-1],index[0]))
        return lambda x: 1.0*get_index(x)
    elif(type_str=="um_nk"):
        um_list, n_list, k_list = list(), list(), list()
        with open(filename) as csv_file:
            reader = csv.reader(csv_file, delimiter = delimiter, 
                                skipinitialspace = True)             
            if(skip_first_line):
                next(reader)
            for row in reader:
                um_list.append(float(row[0]))
                n_list.append(float(row[1]))
                k_list.append(float(row[2]))
        um_array = sp.array(um_list)
        wavelengths = um_array*Units.MICROMETERS
        index = sp.array(n_list) - 1.0j*sp.array(k_list)
        get_index = interpolate.interp1d(wavelengths, index, bounds_error=False,
                                         fill_value=(index[0],index[-1]))
        return lambda x: 1.0*get_index(x)   

def generate_index_from_2csv(filename1, filename2, type_str="nm_nk", 
                             delimiter = ",", skip_first_line = True):
    """Creates a function that returns the index based on a csv file
    
    Arg:
        filename(string): The csv file to be used
        type(string): the type of file to be opened. This can be either:
                        - "eV_Epsilon": stored as eV,er,ei with headings
                        - "um_nk": stored as um,n,k, with headings
        
    Returns:
        callable: returns the complex index given the data in the csv
    """
    if(type_str=="nm_nk"):
        nm_list, n_list = list(), list()
        with open(filename1) as csv_file:
            reader = csv.reader(csv_file, delimiter = delimiter, 
                                skipinitialspace = True)             
            if(skip_first_line):
                next(reader)
            for row in reader:
                nm_list.append(float(row[0]))
                n_list.append(float(row[1]))
        nm_array = sp.array(nm_list)
        wavelengths = nm_array*Units.NANOMETERS
        index = sp.array(n_list)
        get_index_n = interpolate.interp1d(wavelengths, index, bounds_error=False,
                                         fill_value=(index[0],index[-1]))
        nm_list, k_list = list(), list()
        with open(filename2) as csv_file:
            reader = csv.reader(csv_file, delimiter = delimiter, 
                                skipinitialspace = True)             
            if(skip_first_line):
                next(reader)
            for row in reader:
                nm_list.append(float(row[0]))
                k_list.append(float(row[1]))
        nm_array = sp.array(nm_list)
        wavelengths = nm_array*Units.NANOMETERS
        index = - 1.0j*sp.array(k_list)
        get_index_k = interpolate.interp1d(wavelengths, index, bounds_error=False,
                                         fill_value=(index[0],index[-1]))
        
        return lambda x: 1.0*(get_index_n(x)+get_index_k(x))   

def generate_index_from_SOPRA_nk(filename):
    """creates a function that returns an index based on SOPRA nk file data
    
    Arg:
        filename(string): The nk file to be used
                
    Returns:
        callable: returns the complex index given the data in the nk file
    """    
    unit_list, n_list, k_list = list(), list(), list()
    unit_type = 0
    start_unit, end_unit, num_units, inc_units = 0.0,0.0,0.0,0.0
    with open(filename) as csv_file:
        current_row = 0             
        for line in csv_file:
            row = line.split()
            if(current_row == 0):
                unit_type = int(row[0])
                start_unit = float(row[1])
                end_unit = float(row[2])
                num_units = int(row[3])
                inc_units = (end_unit-start_unit)/(num_units-1)
            else:                        
                if(len(row) == 3):
                    unit_list.append(float(row[0]))
                    n_list.append(float(row[1]))
                    k_list.append(float(row[2]))
                else:
                    unit_list.append(start_unit+current_row*inc_units)
                    n_list.append(float(row[0]))
                    k_list.append(float(row[1]))
            current_row += 1
    unit_array = sp.array(unit_list)
    wavelengths = sp.zeros(len(unit_array))
    if(unit_type == 0):
        wavelengths = unit_array*Units.NANOMETERS
    elif(unit_type == 1):
        wavelengths = eV_to_wavelength(unit_array)
    elif(unit_type == 2):
        wavelengths = unit_array*Units.MICROMETERS
    index = sp.array(n_list) - 1.0j*sp.array(k_list)
    fill_indices = (index[0],index[-1])
    if(wavelengths[-1]<wavelengths[0]):
        fill_indices = (index[-1],index[0])        
    get_index = interpolate.interp1d(wavelengths, index, bounds_error=False,
                                     fill_value=fill_indices)
    return get_index 


    
def create_graded_mixed_index(frac_func, x_start, x_end, index_func_1, 
                              index_func_2, num_layers, thickness, 
                              mix_type = "bruggeman"):
    """Creates a multilayer that has a varying mixed medium index
    
    Arg:
        frac_func(callable): A function that takes x as a parameter and returns
                             a value between 0 and 1
        x_start(float): x value for the first layer
        x_end(float): x value for the final layer
        index_func_1(callable): the index returning function of medium 1
        index_func_2(callable): the index returning function of medium 2
        num_layers(int): the number of layers the graded index is to be
                         approximated as
        thickness(float): the thickness of the entire graded index layer
        mix_type (string): the type of approximation formula used
                            - bruggeman: Bruggeman approximation used
                            - MG: Maxwell-Garnett apporximation used
        
    Returns:
        LayerList: resulting multilayer approximating the graded index
    """
    index_list = list()
    thickness_list = list()
    x_inc = (x_end-x_start)/(num_layers-1)
    t_single = thickness/num_layers    
    for i in range(num_layers):
        fraction_1 = frac_func(x_start+i*x_inc)
        index_list.append(generate_mixed_medium_approximation(fraction_1, 
                                                            index_func_1,
                                                            index_func_2,
                                                            mix_type))
        thickness_list.append(t_single)
    return create_multilayer(index_list, thickness_list)    
    
    
"""
------------------------------------
PHOTONIC CALCULATIONS AND STRUCTURES
------------------------------------
"""
        
def scattering_matrix_calculation(structure, wavelengths, incident_angle = 0.0,
                                  mode="TE"):
    """Calculates the T,R, and A of a LayerList using a 1D scattering matrix
    
    Arg:
        structure(LayerList): The multilayer structure for which the 
                              transmission, reflection, and absorption ratios
                              are to be claculated
        wavelengths(float): vacuum wavelength of incident light
        incident_angle(float): propagation angle in the first layer
        mode(string): mode of the incident wave. This can be either "TE" or "TM"
        
    Returns:
        float,float,float,float,float,float: the transmission, reflection, 
                                             absorption, wavelengths,
                                             incident angle, and mode
        
    Note: wavelengths can also be an np.array
    """
    num_steps = len(wavelengths)
    num_layers = len(structure)
    angles = np.zeros([num_layers, num_steps], dtype=np.complex)
    indexes = np.zeros([num_layers, num_steps], dtype=np.complex)
    phase_shifts = np.zeros([num_layers, num_steps], dtype=np.complex)
        
    indexes[0] = structure[0].get_index(wavelengths)
    angles[0] = np.ones(num_steps)*incident_angle
    phase_shifts[0] = (np.exp(-1.0j*get_kz(indexes[0], angles[0], wavelengths)
                      *structure[0].thickness))
    
    for i in range(1, num_layers):
        indexes[i] = structure[i].get_index(wavelengths)
        angles[i] = transmission_angle(indexes[i-1], indexes[i], angles[i-1])
        phase_shifts[i] = (np.exp(-1.0j
                          *get_kz(indexes[i], angles[i], wavelengths)
                          *structure[i].thickness))  
    
    S11 = np.ones(num_steps)
    S12 = np.zeros(num_steps)
    S21 = np.zeros(num_steps)
    S22 = np.ones(num_steps)         
    
    reflection_func = reflection_TE
    transmission_func = transmission_TE
    
    if(mode == "TM"):
        reflection_func = reflection_TM
        transmission_func = transmission_TM
    
    for i in range(num_layers-1):
        index_of_current_layer = indexes[i]
        index_of_next_layer = indexes[i+1]
        reflection_at_boundary = reflection_func(index_of_current_layer, 
                                                 index_of_next_layer, 
                                                 angles[i])        
        transmission_at_boundary = transmission_func(index_of_current_layer,
                                                     index_of_next_layer, 
                                                     angles[i])
        I11 = 1.0/transmission_at_boundary
        I12 = reflection_at_boundary/transmission_at_boundary
        I21 = I12
        I22 = I11
        S11 = (phase_shifts[i]*S11)/(I11 - phase_shifts[i]*S12*I21)
        S12 = (((phase_shifts[i]*S12*I22-I12)*phase_shifts[i+1])
              /(I11-phase_shifts[i]*S12*I21))
        S21 = S22*I21*S11+S21
        S22 = S22*I21*S12+S22*I22*phase_shifts[i+1]
    
    transmission_of_stack = np.absolute(S11*np.conj(S11)*indexes[num_layers-1]
                                        *np.cos(angles[num_layers-1])
                                        /(indexes[0]*np.cos(angles[0])))
    reflection_of_stack = np.absolute(S21*np.conj(S21))
    absorption_of_stack = 1.0-transmission_of_stack-reflection_of_stack
    return transmission_of_stack, reflection_of_stack, absorption_of_stack, \
    wavelengths, incident_angle, mode  