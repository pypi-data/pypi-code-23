#!/usr/bin/env python

"""
Reads and draws images for all GalFit FITS files in directory
"""
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
# "Nicer set of plot parameters"
from astropy.visualization import astropy_mpl_style
from astropy.io import fits
import numpy as np
import glob
import a99
import ariastro
import argparse
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True


# TODO add pre-processing options from command-line
def preprocess(image):
    """This function takes a grayscale image (matrix) and performs operation to improve visualization"""

    return np.power(image, 0.2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('-w', '--width', type=int, nargs='?', default=1000,
        help="Output image width (pixels)")
    args = parser.parse_args()

    filenames = glob.glob("*.fits")

    for filename in filenames:
        print("Processing file '{}'...".format(filename))
        try:
            imgfilename = filename+".png"

            f = ariastro.FileGalfit()
            f.load(filename)
            
            ariastro.draw_galfit_tiles(f, image_width=args.width, preprocessing=preprocess)

            plt.savefig(imgfilename)
            print("Saved file '{}'".format(imgfilename))
            plt.close()
            
        except Exception as e:
            msg = "Error processing file '{}': '{}'".format(filename, str(e))
            a99.get_python_logger().exception(msg)
            print(msg)
