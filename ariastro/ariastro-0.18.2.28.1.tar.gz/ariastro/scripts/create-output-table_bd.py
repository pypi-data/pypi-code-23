#!/usr/bin/env python
"""
This script should be probably run from the 'outputs' directory or similar
"""

import numpy as np

from astropy.io import fits
from collections import OrderedDict
import glob
import os
import re
import multiprocessing as mp
from ariastro import *

def read_output_bd(filename):
    """
    Not useful anymore, read_output.py does everything

    Reads FITS file and extracts selected information from fifth frame header

    Returns: dictionary with keys as in sample header below, with the initial "2_" replaced by
             "B_" as in "Bulge"

    2_XC_U  = '249.2548 +/- 0.0382' / X center [pixel]
    2_XC_G  = '249.6460 +/- 0.0382' / X center [pixel]
    2_XC_R  = '248.8654 +/- 0.0382' / X center [pixel]
    2_XC_I  = '248.8550 +/- 0.0382' / X center [pixel]
    2_XC_Z  = '249.0299 +/- 0.0382' / X center [pixel]
    2_YC_U  = '249.3147 +/- 0.0516' / Y center [pixel]
    2_YC_G  = '249.4742 +/- 0.0516' / Y center [pixel]
    2_YC_R  = '249.0633 +/- 0.0516' / Y center [pixel]
    2_YC_I  = '249.1092 +/- 0.0516' / Y center [pixel]
    2_YC_Z  = '249.0897 +/- 0.0516' / Y center [pixel]
    2_MAG_U = '19.3482 +/- 0.1520' / Integrated magnitude [mag]
    2_MAG_G = '17.9082 +/- 0.0691' / Integrated magnitude [mag]
    2_MAG_R = '16.5893 +/- 0.0465' / Integrated magnitude [mag]
    2_MAG_I = '15.5702 +/- 0.0393' / Integrated magnitude [mag]
    2_MAG_Z = '13.4458 +/- 0.0312' / Integrated magnitude [mag]
    2_RE_U  = '8.3340 +/- 1.1544'  / Effective radius Re [pixels]
    2_RE_G  = '7.7037 +/- 0.6040'  / Effective radius Re [pixels]
    2_RE_R  = '7.7923 +/- 0.4497'  / Effective radius Re [pixels]
    2_RE_I  = '8.7270 +/- 0.4563'  / Effective radius Re [pixels]
    2_RE_Z  = '10.6748 +/- 0.4463' / Effective radius Re [pixels]
    2_N_U   = '1.5647 +/- 0.2898'  / Sersic index
    2_N_G   = '1.9657 +/- 0.1551'  / Sersic index
    2_N_R   = '2.2742 +/- 0.1139'  / Sersic index
    2_N_I   = '2.3974 +/- 0.1062'  / Sersic index
    2_N_Z   = '2.3424 +/- 0.0838'  / Sersic index
    2_AR_U  = '0.6018 +/- 0.0082'  / Axis ratio (b/a)
    2_AR_G  = '0.6018 +/- 0.0082'  / Axis ratio (b/a)
    2_AR_I  = '0.6018 +/- 0.0082'  / Axis ratio (b/a)
    2_AR_Z  = '0.6018 +/- 0.0082'  / Axis ratio (b/a)
    2_AR_R  = '0.6018 +/- 0.0082'  / Axis ratio (b/a)
    2_PA_U  = '-34.6905 +/- 1.0838' / Position Angle (PA) [degrees: Up=0, Left=90]
    2_PA_G  = '-34.6905 +/- 1.0838' / Position Angle (PA) [degrees: Up=0, Left=90]
    2_PA_R  = '-34.6905 +/- 1.0838' / Position Angle (PA) [degrees: Up=0, Left=90]
    2_PA_I  = '-34.6905 +/- 1.0838' / Position Angle (PA) [degrees: Up=0, Left=90]
    2_PA_Z  = '-34.6905 +/- 1.0838' / Position Angle (PA) [degrees: Up=0, Left=90]
    COMMENT ------------------------------------------------------------------------
    3_XC_U  = '248.6784 +/- 0.1768' / X center [pixel]
    3_XC_G  = '249.0696 +/- 0.1768' / X center [pixel]
    3_XC_R  = '248.2890 +/- 0.1768' / X center [pixel]
    3_XC_I  = '248.2786 +/- 0.1768' / X center [pixel]
    3_XC_Z  = '248.4535 +/- 0.1768' / X center [pixel]
    3_YC_U  = '248.9206 +/- 0.2522' / Y center [pixel]
    3_YC_G  = '249.0801 +/- 0.2522' / Y center [pixel]
    3_YC_R  = '248.6692 +/- 0.2522' / Y center [pixel]
    3_YC_I  = '248.7151 +/- 0.2522' / Y center [pixel]
    3_YC_Z  = '248.6956 +/- 0.2522' / Y center [pixel]
    3_MAG_U = '19.0583 +/- 0.1125' / Integrated magnitude
    3_MAG_G = '17.2588 +/- 0.0366' / Integrated magnitude
    3_MAG_R = '15.9627 +/- 0.0238' / Integrated magnitude
    3_MAG_I = '15.0478 +/- 0.0225' / Integrated magnitude
    3_MAG_Z = '13.3756 +/- 0.0270' / Integrated magnitude
    3_RS_U  = '14.4636 +/- 0.4146' / Scalelength [pixels]
    3_RS_G  = '17.4697 +/- 0.2682' / Scalelength [pixels]
    3_RS_R  = '21.0490 +/- 0.1447' / Scalelength [pixels]
    3_RS_I  = '24.4642 +/- 0.2031' / Scalelength [pixels]
    3_RS_Z  = '28.1612 +/- 0.3731' / Scalelength [pixels]
    3_AR_U  = '0.6051 +/- 0.0054'  / Axis ratio (b/a)
    3_AR_G  = '0.6051 +/- 0.0054'  / Axis ratio (b/a)
    3_AR_R  = '0.6051 +/- 0.0054'  / Axis ratio (b/a)
    3_AR_I  = '0.6051 +/- 0.0054'  / Axis ratio (b/a)
    3_AR_Z  = '0.6051 +/- 0.0054'  / Axis ratio (b/a)
    3_PA_U  = '5.9352 +/- 0.6999'  / Position Angle (PA) [degrees: Up=0, Left=90]
    3_PA_G  = '5.9352 +/- 0.6999'  / Position Angle (PA) [degrees: Up=0, Left=90]
    3_PA_R  = '5.9352 +/- 0.6999'  / Position Angle (PA) [degrees: Up=0, Left=90]
    3_PA_I  = '5.9352 +/- 0.6999'  / Position Angle (PA) [degrees: Up=0, Left=90]
    3_PA_Z  = '5.9352 +/- 0.6999'  / Position Angle (PA) [degrees: Up=0, Left=90]

    >>> ret = read_output_bd("CGCG163-062_bd.fits")
    >>> print(ret)
    OrderedDict([('2_XC_G', '[146.4001]'), ('2_XC_R', '[149.6384]'), ('2_XC_I', '[146.7359]'), ('2_YC_G', '[139.9570]'), ('2_YC_R', '[150.7310]'), ('2_YC_I', '[143.6689]'), ('2_MAG_G', '15.7492 +/- 0.0026'), ('2_MAG_R', '15.6563 +/- 0.0024'), ('2_MAG_I', '15.0261 +/- 0.0030'), ('2_RE_G', '27.5178 +/- 0.0701'), ('2_RE_R', '27.9453 +/- 0.0505'), ('2_RE_I', '28.3532 +/- 0.0839'), ('2_N_G', '0.7177 +/- 0.0051'), ('2_N_R', '0.7633 +/- 0.0035'), ('2_N_I', '0.8069 +/- 0.0060'), ('2_AR_G', '0.9221 +/- 0.0014'), ('2_AR_R', '0.9221 +/- 0.0014'), ('2_AR_I', '0.9221 +/- 0.0014'), ('2_PA_G', '-64.7095 +/- 1.0063'), ('2_PA_R', '-64.7095 +/- 1.0063'), ('2_PA_I', '-64.7095 +/- 1.0063')])
    """

    fields_to_extract = ["2_XC_U", "2_XC_G", "2_XC_R", "2_XC_I", "2_XC_Z", "2_YC_U", "2_YC_G", "2_YC_R", "2_YC_I",
                         "2_YC_Z", "2_MAG_U", "2_MAG_G",
                         "2_MAG_R", "2_MAG_I", "2_MAG_Z", "2_RE_U", "2_RE_G", "2_RE_R", "2_RE_I", "2_RE_Z", "2_N_U",
                         "2_N_G", "2_N_R",
                         "2_N_I", "2_N_Z", "2_AR_U", "2_AR_G", "2_AR_R", "2_AR_I", "2_AR_Z", "2_PA_U", "2_PA_G",
                         "2_PA_R", "2_PA_I", "2_PA_Z",
                         "1_SKY_0", "1_SKY_1", "1_SKY_2", "1_SKY_3", "1_SKY_4", "3_XC_U", "3_XC_G", "3_XC_R", "3_XC_I",
                         "3_XC_Z", "3_YC_U", "3_YC_G", "3_YC_R", "3_YC_I", "3_YC_Z", "3_MAG_U", "3_MAG_G",
                         "3_MAG_R", "3_MAG_I", "3_MAG_Z", "3_RS_U", "3_RS_G", "3_RS_R", "3_RS_I", "3_RS_Z", "3_AR_U",
                         "3_AR_G", "3_AR_R", "3_AR_I", "3_AR_Z", "3_PA_U", "3_PA_G", "3_PA_R", "3_PA_I",
                         "3_PA_Z"]
    hdulist = fits.open(filename)

    ret = OrderedDict()
    flag_invalid = False  # will be set to True if any values has a "*"
    for name in fields_to_extract:
        expr = hdulist[7].header[name]
        # if expr.startswith("*"):
        if "*" in expr:
            msg = "Invalid value for header '{}': '{}'".format(name, expr)
            raise RuntimeError(msg)
            # flag_invalid = True
            # break
            # print expr, name, filename
            # continue

        # Matches pattern such as '15.7492 +/- 0.0026'
        gg = re.match("([0-9.-]+)\s*\+/-\s*([0-9.-]+)", expr)

        if gg is not None:
            value, error = gg.groups()
            # We know that it is a (value, error) pair
            # print expr

        elif expr.startswith("["):
            value = expr.strip()[1:-1]
            error = '0.'
        else:
            value = expr
            error = '0.'

        ret[name] = value
        ret[name + "_ERROR"] = error

    hdulist.close()

    # if flag_invalid:
    #    return None

    return ret

def create_output_table_bd(dir_=".", output_filename="output-mega-califa_bd.txt"):
    """
    Reads all files in directory specified and saves as a txt file

    Returns: number of fits files written

    >>> create_output_table_bd(".")
    3
    """

    files = glob.glob(os.path.join(dir_, "*.fits"))
    print(files)
    n = 0
    with open(os.path.join(dir_, output_filename), "w") as out:
        for filename in files:
            galaxy_name = os.path.split(filename)[1].split("_")[0]

            try:
                data = read_output_bd(filename)
            except Exception as e:
                msg = "Error dealing with file '{}': {}: {}".format(filename, e.__class__.__name__, str(e))
                print(msg)
                write_bad_fit(galaxy_name, msg)
                continue

            # data = read_output_chi2(filename)

            if n == 0:
                out.write("#" " " + "galaxy_name" + " " + " ".join(list(data.keys())) + "\n")

            out.write(galaxy_name + " " + " ".join(list(data.values())) + "\n")

            n += 1

    return n


if __name__ == "__main__":
    create_output_table_bd(".")