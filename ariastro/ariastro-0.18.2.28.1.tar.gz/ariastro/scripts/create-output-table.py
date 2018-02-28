#!/usr/bin/env python
"""
This script should be probably run from the 'outputs' directory or similar
"""

from astropy.io import fits
from collections import OrderedDict
import glob
import os
import multiprocessing as mp


def read_output(filename):
    """
    Reads FITS file and extracts selected information from penultimate frame data

    Returns:
        dictionary: a "flattened" version of the table data in the penultimate frame of the FITS file.
                    The keys are <original field name in numpy array>_<band letter>, for example: "COMP1_XC_U"
                    (field was "COMP1_XC" and band is "U")


    hdulist[-2].data sample:

        FITS_rec([ ('u', 430.0, 0.0, 0, 430.0, 0.0, 0, -0.0012000001, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 430.76367, 0.43971181, 1, 437.45587, 2.3212292, 1, 18.2036, 0.039023668, 1, 70.497238, 1.6941882, 1, 0.33186108, 0.025464246, 1, 0.19848995, 0.0050456659, 1, 1.8755809, 0.40784442, 1),
                   ('g', 430.0, 0.0, 0, 430.0, 0.0, 0, -0.00066999998, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 430.4393, 0.26242495, 1, 438.08072, 1.1981732, 1, 17.397177, 0.020027174, 1, 68.003441, 0.8296113, 1, 0.41161668, 0.011642374, 1, 0.22190171, 0.0025764173, 1, 2.1990237, 0.21120539, 1),
                   ('r', 430.0, 0.0, 0, 430.0, 0.0, 0, -0.00023000001, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 429.79575, 0.22847107, 1, 435.85583, 1.0234721, 1, 16.614887, 0.016775975, 1, 64.772774, 0.56382304, 1, 0.50353318, 0.010757586, 1, 0.23668186, 0.0020852997, 1, 2.4045742, 0.17398277, 1),
                   ('i', 430.0, 0.0, 0, 430.0, 0.0, 0, -0.00211, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 430.63159, 0.18267216, 1, 435.00528, 0.76906836, 1, 15.907736, 0.014295106, 1, 61.425461, 0.57469875, 1, 0.58814436, 0.010949646, 1, 0.23751204, 0.0020082004, 1, 2.4187121, 0.16746925, 1),
                   ('z', 430.0, 0.0, 0, 430.0, 0.0, 0, -0.00056999997, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0, 430.80585, 0.17817506, 1, 432.51694, 0.80425751, 1, 14.291779, 0.016046198, 1, 57.510559, 0.84336847, 1, 0.67633432, 0.02100935, 1, 0.22380203, 0.0031048364, 1, 2.2337053, 0.25965932, 1)],
                  dtype=(numpy.record, [('BAND', 'S17'), ('COMP1_XC', '>f4'), ('COMP1_XC_ERR', '>f4'), ('COMP1_XC_FIT', '>i4'), ('COMP1_YC', '>f4'), ('COMP1_YC_ERR', '>f4'), ('COMP1_YC_FIT', '>i4'), ('COMP1_SKY', '>f4'), ('COMP1_SKY_ERR', '>f4'), ('COMP1_SKY_FIT', '>i4'), ('COMP1_DSDX', '>f4'), ('COMP1_DSDX_ERR', '>f4'), ('COMP1_DSDX_FIT', '>i4'), ('COMP1_DSDY', '>f4'), ('COMP1_DSDY_ERR', '>f4'), ('COMP1_DSDY_FIT', '>i4'), ('COMP2_XC', '>f4'), ('COMP2_XC_ERR', '>f4'), ('COMP2_XC_FIT', '>i4'), ('COMP2_YC', '>f4'), ('COMP2_YC_ERR', '>f4'), ('COMP2_YC_FIT', '>i4'), ('COMP2_MAG', '>f4'), ('COMP2_MAG_ERR', '>f4'), ('COMP2_MAG_FIT', '>i4'), ('COMP2_Re', '>f4'), ('COMP2_Re_ERR', '>f4'), ('COMP2_Re_FIT', '>i4'), ('COMP2_n', '>f4'), ('COMP2_n_ERR', '>f4'), ('COMP2_n_FIT', '>i4'), ('COMP2_AR', '>f4'), ('COMP2_AR_ERR', '>f4'), ('COMP2_AR_FIT', '>i4'), ('COMP2_PA', '>f4'), ('COMP2_PA_ERR', '>f4'), ('COMP2_PA_FIT', '>i4')]))

    Usage example:

        >>> ret = read_output("CGCG163-062_ss.fits")
        >>> print(ret)
        TODO get output and paste here
    """

    print(("Processing file '{}'".format(filename)))

    hdulist = fits.open(filename)
    data = hdulist[-2].data
    fields_to_extract = [field_name for field_name, __ in data.dtype.descr][1:]
    band_names = [x.upper() for x in data["BAND"]]

    ret = OrderedDict()
    for field_name in fields_to_extract:
        for i, band_name in enumerate(band_names):
            ret[field_name+"_"+band_name] = data[i][field_name]

    hdulist.close()

    return ret


def create_output_table(dir_=".", output_filename="output-mega-califa.txt"):
    """
    Reads all files in directory specified and saves as a txt file

    Returns: number of fits files written

    >>> create_output_table(".")
    3
    """

    filenames = glob.glob(os.path.join(dir_, "*.fits"))

    p = mp.Pool(8)
    rows = p.map(read_output, filenames)

    num_files = len(filenames)
    # print files
    n = 0
    with open(os.path.join(dir_, output_filename), "w") as out:
        for filename, data in zip(filenames, rows):
            galaxy_name = os.path.split(filename)[1].split("_")[0]

            if n == 0:
                out.write("#" " " + "galaxy_name" + " " + " ".join(list(data.keys())) + "\n")

            out.write(galaxy_name + " " + " ".join([str(x) for x in list(data.values())]) + "\n")

            n += 1

            if n % 10 == 0:
                print(("Processed {}/{} files".format(n, num_files)))

    return n


if __name__ == "__main__":
    create_output_table(".")
