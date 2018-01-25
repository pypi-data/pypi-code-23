import numpy as np
from ubm.acquisition.dataset.names import Names
from ubm.acquisition.filter import Filter


class Cylinders:

    LAMBDA = Names.Engine['Cylinder']['Lambda']

    def __init__(self):
        self.cylinders = (Cylinder(1), Cylinder(2), Cylinder(3), Cylinder(4))

    def get(self, number):
        return self.cylinders[number]


class Cylinder:

    def __init__(self, number):
        self.number = number

    def get_injected_mass(self):
        return