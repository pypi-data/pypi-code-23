import numpy as np

from astropy.io import fits
from collections import OrderedDict
import glob
import os
import re
import multiprocessing as mp

__all__ = ["FILENAME_NOT_RUN", "FILENAME_BAD_FIT", "isolate_code", "write_not_run", "write_bad_fit",
           "get_dims", "get_exptime", "get_x0y0", "load_jma_gri", "find_row_by_galaxy_name",
           "find_row_by_galaxy_name2", "dump_header", "solve_feedme_template", "get_output_pattern",
           "fromNMAGYtoCOUNTs", ]


FILENAME_NOT_RUN = "not-run.csv"
FILENAME_BAD_FIT = "bad-fit.csv"

_file_not_run = None
_file_bad_fit = None

def get_file_not_run():
    """Gets "not_run" file object. Opens file at first call, otherwire returns open file"""
    global _file_not_run
    if _file_not_run is None:
        _file_not_run = open(FILENAME_NOT_RUN, "w")
    return _file_not_run


def get_file_bad_fit():
    """Gets "bad_fit" file object. Opens file at first call, otherwire returns open file"""
    global _file_bad_fit
    if _file_bad_fit is None:
        _file_bad_fit = open(FILENAME_BAD_FIT, "w")
    return _file_bad_fit


def isolate_code():
    """Exits the program showing message. Easy way to protect test/conversion scripts from running again"""
    import sys

    sys.exit("\n\nNot running this program again, sorry. \n\n"
             "This program was designed to run only once.\n\n")


def write_not_run(galaxy_name, s):
    """Writes line to "not run" log file"""
    get_file_not_run().write('%-40s,"%s"\n' % (galaxy_name, s))


def write_bad_fit(galaxy_name, s):
    """Writes line to "bad fit" log file"""
    get_file_bad_fit().write('%-40s,"%s"\n' % (galaxy_name, s))


def get_dims(filename):
    """Returns a tuple (width, height)"""
    hdulist = fits.open(filename)
    hdu = hdulist[0]
    ret = (hdu.header["NAXIS1"], hdu.header["NAXIS2"])
    hdulist.close()
    return ret


def get_exptime(filename):
    """Returns exposure-time from image header"""
    hdulist = fits.open(filename)
    hdu = hdulist[0]
    ret = hdu.header["EXPTIME"]
    hdulist.close()
    return ret


def get_x0y0(filename):
    """Returns x0,y0 from image header"""
    hdulist = fits.open(filename)
    hdu = hdulist[0]
    ret = (hdu.header["OBJXPIX"],hdu.header["OBJYPIX"])
    hdulist.close()
    return ret
                        


def load_jma_gri(filename):
    """Loads a file such as CALIFA-JMA-gri.mfmtk (it is a CSV file)

    Returns:
         list of OrderedDict()
    """

    ret = []

    with open(filename, "r") as f:
        s = f.readline().strip()[1:].strip()

        fieldnames = s.split(",")

        for line in f:
            fieldvalues = line.strip().split(",")

            row = OrderedDict()
            for key, value in zip(fieldnames, fieldvalues):
                row[key] = value
            ret.append(row)
    return ret


def find_row_by_galaxy_name(table, galaxy_name, fieldname="rootname69_u"):
    """
    Searches for galaxy name in table

    Args:
        table: list of dictionaries
        fieldname="rootname69_u": field to be considered the galaxy name
        galaxy_name: string

    Returns:
        table row (dictionary), or None if not found
    """

    ret = None
    for row in table:
        if row[fieldname] == galaxy_name:
            ret = row
            break
    return ret


def find_row_by_galaxy_name2(table, galaxy_name):
    return find_row_by_galaxy_name(table, galaxy_name, "galaxy_name")


def dump_header(filename):
    """
    Reads FITS file and dumps all headers into a text file named <filename>.txt
    """

    def dump(s):
        f.write(s+"\n")
        print(s)

    hdulist = fits.open(filename)

    output_filename = filename + ".txt"

    print("\n===BEGIN===")
    with open(output_filename, "w") as f:
        i = 0
        for hdu in hdulist:
            if i > 0:
                dump("\n\n")
            dump("***** FRAME %02d *****" % i)
            dump(repr(hdu.header))
            i += 1
    print("===END===")

    n = len(hdulist)
    print("\nWrote {} frame{} to file '{}'".format(n, "" if n == 1 else "s", output_filename))


def fromNMAGYtoCOUNTs(dir_="."):
    """Transforms NMAGYS into counts for both PSFS and images"""

    ff = glob.glob(os.path.join(dir_, "*.fits"))
    # file_names=[]
    # for f in ff

    # filename = os.path.basaname(f)
    # pieces = filename.split("_")
    # file_name = pieces[1]
    # file_names.append(f)

    # file_names = list(set(file_names))


    for file_name in ff:
        print("Converting {}".format(file_name))
        hdulist = fits.open(file_name)

        med = np.mean(hdulist[0].data)
        print("Mmmmmmmmmmmmm {}".format(med))
        hdulist[0].data /= 0.00449599

        os.unlink(file_name)

        hdulist.writeto(file_name)
        hdulist.close()


####################################################################################################
#   _____          _      ______ _____ _______
#  / ____|   /\   | |    |  ____|_   _|__   __| http://patorjk.com/software/taag/#p=display&f=Big&t=GALFIT
# | |  __   /  \  | |    | |__    | |    | |
# | | |_ | / /\ \ | |    |  __|   | |    | |
# | |__| |/ ____ \| |____| |     _| |_   | |
#  \_____/_/    \_\______|_|    |_____|  |_|
# GALFIT TEMPLATE HANDLING
#


def solve_feedme_template(template, search_replace):
    """
    Replaces all patterns in template text, returning a (hopefully) sane GALFIT FEEDME text

    Args:
        template: template text
        search_replace: [(search0, replace0), (search1, replace1), ...], i.e., search-replace pairs

    Returns:
        str: contents
    """

    contents = template
    for pattern, str_replace in search_replace:
        contents = contents.replace(pattern, str_replace)

    return contents


def get_output_pattern(template):
    """Tries to figure out (extract) the output filename pattern from inside the template

    Returns:
        str: output pattern containing string "@@@@@@"

    I am looking for a line in galfit.feedme.template that looks like

    ```
    B) ../outputs/@@@@@@_ss.fits       # Output data image block
    ```
    """

    for line in template.split("\n"):
        if line.startswith("B)"):
            pieces = line.split(" ")
            ret = pieces[1].strip()
            print("Found output filename pattern: '{}'".format(ret))
            if "@@@@@@" in ret:
                return ret

    raise RuntimeError("Could not figure out output pattern, sorry, gotta find new solution for this")
