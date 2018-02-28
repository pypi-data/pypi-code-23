#!/usr/bin/env python
"""
Reads and draws images for all fits files in directory

Run with python3 !

"""
import matplotlib

matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
# "Nicer set of plot parameters"
from astropy.visualization import astropy_mpl_style
from astropy.io import fits
import numpy as np
import glob
import f311.filetypes as ft
import f311.explorer as ex
import a99
import sys
import ariastro

if __name__ == "__main__":
    
    filenames = glob.glob("*.fits")

    for filename in filenames:
        print("Processing file '{}'...".format(filename))
        try:
            imgfilename = filename + ".png"

            f = ft.FileGalfit()
            f.load(filename)

            ex.draw_galfit_tiles(f, 2000)
            plt.show()

            break

        except Exception as e:
            msg = "Error processing file '{}': '{}'".format(filename, str(e))
            a99.get_python_logger().exception(msg)
            print(msg)

